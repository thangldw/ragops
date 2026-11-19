"""Counterfactual-evidence test: does the answer actually depend on the evidence?

For each case the evidence is altered in a controlled way and *your own system* is asked again
(``--answer-command``). A grounded answer must react: lose what the removed passage supported, or
repeat the changed number. An answer that stays the same (or keeps the old number) was not coming
from the evidence at all, which a similarity score against the original evidence cannot show.

No labels and no model are needed here; the cost is calling your system once per altered case.
Redundant evidence (two passages stating the same fact) can make a faithful answer look unchanged,
so treat flagged cases as leads to read.
"""

from __future__ import annotations

import json
import math
import re
import subprocess
from dataclasses import asdict, dataclass, field
from typing import Any

from ragops.evaluators import tokenize
from ragops.loader import ContractError
from ragops.models import EvalCase, RecordedResponse

PERTURBATIONS = ("remove_support", "swap_number")
NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)*")
MAX_OUTPUT_BYTES = 100_000
SUPPORT_OVERLAP = 0.25


@dataclass(frozen=True)
class CaseCheck:
    case_id: str
    perturbation: str
    status: str  # sensitive | insensitive | skipped
    detail: str
    new_answer: str = ""


@dataclass(frozen=True)
class PerturbationSummary:
    perturbation: str
    eligible: int
    insensitive: int
    skipped: int
    insensitive_rate: float


@dataclass(frozen=True)
class CounterfactualReport:
    schema_version: str
    scenario_id: str
    decision: str  # PASS | BLOCK | INCONCLUSIVE
    max_insensitive_rate: float
    min_eligible: int
    same_threshold: float
    summaries: tuple[PerturbationSummary, ...]
    checks: tuple[CaseCheck, ...]
    failed_gates: tuple[str, ...] = field(default=())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CommandAnswerer:
    """Run an explicit command (no shell) per altered case.

    stdin:  {"case_id": str, "question": str, "evidence": [str, ...]}
    stdout: {"answer": str}
    """

    def __init__(self, command: tuple[str, ...], *, timeout_seconds: float = 60.0) -> None:
        if not command or any(not isinstance(part, str) or not part for part in command):
            raise ValueError("Answer command must contain non-empty arguments")
        if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("Answer command timeout must be finite and positive")
        self.command = command
        self.timeout_seconds = timeout_seconds

    def answer(self, case_id: str, question: str, evidence: list[str]) -> str:
        payload = json.dumps({"case_id": case_id, "question": question, "evidence": evidence}, ensure_ascii=False)
        try:
            completed = subprocess.run(
                self.command, input=payload.encode("utf-8"), capture_output=True, check=False,
                timeout=self.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ContractError(f"Answer command failed for {case_id}: {exc}") from exc
        if completed.returncode != 0:
            error = completed.stderr[:2000].decode("utf-8", errors="replace").strip()
            raise ContractError(f"Answer command exited {completed.returncode} for {case_id}: {error}")
        if len(completed.stdout) > MAX_OUTPUT_BYTES:
            raise ContractError("Answer command output is too large")
        try:
            value = json.loads(completed.stdout.decode("utf-8"))["answer"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ContractError('Answer command must print {"answer": text}') from exc
        if not isinstance(value, str):
            raise ContractError("Answer command answer must be text")
        return value


def _support_indexes(evidence: tuple[str, ...], answer: str) -> list[int]:
    answer_tokens = tokenize(answer)
    if not answer_tokens:
        return []
    overlaps = [len(answer_tokens & tokenize(passage)) / len(answer_tokens) for passage in evidence]
    best = max(overlaps, default=0.0)
    if best == 0:
        return []
    chosen = [i for i, value in enumerate(overlaps) if value >= SUPPORT_OVERLAP]
    return chosen or [overlaps.index(best)]


def _jaccard(first: str, second: str) -> float:
    a, b = tokenize(first), tokenize(second)
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def _changed_number(token: str) -> str:
    plain = token.replace(",", "")
    if "." in plain:
        decimals = len(plain.split(".")[1])
        return f"{float(plain) * 7 + 13:.{decimals}f}"
    return str(int(plain) * 7 + 13)


def _check_remove_support(
    case: EvalCase, baseline: str, answerer: CommandAnswerer, same_threshold: float
) -> CaseCheck:
    drop = _support_indexes(case.evidence, baseline)
    if not drop:
        return CaseCheck(case.id, "remove_support", "skipped", "no evidence passage supports the baseline answer")
    kept = [passage for i, passage in enumerate(case.evidence) if i not in drop]
    new_answer = answerer.answer(case.id, case.question, kept)
    similarity = _jaccard(baseline, new_answer)
    if similarity >= same_threshold:
        return CaseCheck(
            case.id, "remove_support", "insensitive",
            f"answer barely changed (similarity {similarity:.2f}) after removing {len(drop)} supporting passage(s)",
            new_answer,
        )
    return CaseCheck(case.id, "remove_support", "sensitive", f"answer changed (similarity {similarity:.2f})", new_answer)


def _check_swap_number(case: EvalCase, baseline: str, answerer: CommandAnswerer) -> CaseCheck:
    in_evidence = set(NUMBER_RE.findall(" ".join(case.evidence)))
    asked = set(NUMBER_RE.findall(case.question))
    swapped = {n: _changed_number(n) for n in sorted(set(NUMBER_RE.findall(baseline)) & in_evidence - asked)}
    if not swapped:
        return CaseCheck(case.id, "swap_number", "skipped", "the answer states no number taken from the evidence")
    evidence = [NUMBER_RE.sub(lambda m: swapped.get(m.group(0), m.group(0)), passage) for passage in case.evidence]
    new_answer = answerer.answer(case.id, case.question, evidence)
    present = set(NUMBER_RE.findall(new_answer))
    stuck = sorted(old for old in swapped if old in present)
    if stuck:
        return CaseCheck(
            case.id, "swap_number", "insensitive",
            f"still states {', '.join(stuck)} although the evidence now says {', '.join(swapped[o] for o in stuck)}",
            new_answer,
        )
    return CaseCheck(case.id, "swap_number", "sensitive", "the old number is gone from the answer", new_answer)


def run_counterfactual(
    scenario_id: str,
    cases: tuple[EvalCase, ...],
    responses: dict[str, RecordedResponse],
    answerer: CommandAnswerer,
    *,
    perturbations: tuple[str, ...] = PERTURBATIONS,
    same_threshold: float = 0.8,
    max_insensitive_rate: float = 0.2,
    min_eligible: int = 3,
    limit: int | None = None,
) -> CounterfactualReport:
    unknown = sorted(set(perturbations) - set(PERTURBATIONS))
    if unknown or not perturbations:
        raise ContractError(f"Perturbations must be chosen from {PERTURBATIONS}, got {unknown or 'none'}")
    for name, value in (("same_threshold", same_threshold), ("max_insensitive_rate", max_insensitive_rate)):
        if isinstance(value, bool) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ContractError(f"{name} must be between 0 and 1")
    if min_eligible < 1 or (limit is not None and limit < 1):
        raise ContractError("min_eligible and limit must be at least 1")
    selected = cases[:limit] if limit else cases
    checks: list[CaseCheck] = []
    for case in selected:
        response = responses.get(case.id)
        if response is None:
            raise ContractError(f"No recorded response for case {case.id!r}")
        for perturbation in perturbations:
            if perturbation == "remove_support":
                checks.append(_check_remove_support(case, response.answer, answerer, same_threshold))
            else:
                checks.append(_check_swap_number(case, response.answer, answerer))
    summaries, failed, inconclusive = [], [], []
    for perturbation in perturbations:
        mine = [c for c in checks if c.perturbation == perturbation]
        eligible = [c for c in mine if c.status != "skipped"]
        bad = sum(c.status == "insensitive" for c in eligible)
        rate = bad / len(eligible) if eligible else 0.0
        summaries.append(PerturbationSummary(perturbation, len(eligible), bad, len(mine) - len(eligible), rate))
        if len(eligible) < min_eligible:
            inconclusive.append(f"too_few_cases:{perturbation}")
        elif rate > max_insensitive_rate:
            failed.append(f"insensitive_rate:{perturbation}")
    decision = "BLOCK" if failed else "INCONCLUSIVE" if inconclusive else "PASS"
    return CounterfactualReport(
        "1.0", scenario_id, decision, max_insensitive_rate, min_eligible, same_threshold,
        tuple(summaries), tuple(checks), tuple(failed + inconclusive),
    )


def counterfactual_markdown(report: CounterfactualReport) -> str:
    lines = [
        f"## RAGOps counterfactual-evidence test: {report.decision}",
        "",
        f"Scenario: `{report.scenario_id}`. Evidence was altered and your system asked again; "
        f"at most {report.max_insensitive_rate:.0%} of eligible cases may ignore the change "
        f"(at least {report.min_eligible} eligible cases are needed to conclude).",
        "",
        "| Perturbation | Eligible | Ignored the change | Rate | Skipped |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for item in report.summaries:
        lines.append(
            f"| `{item.perturbation}` | {item.eligible} | {item.insensitive} | {item.insensitive_rate:.0%} | {item.skipped} |"
        )
    flagged = [c for c in report.checks if c.status == "insensitive"]
    if flagged:
        lines += ["", "Cases whose answer ignored the altered evidence (read these first):", ""]
        for check in flagged[:20]:
            case_id = check.case_id.replace("`", "\\`").replace("|", "\\|")
            lines.append(f"- `{case_id}` ({check.perturbation}): {check.detail}")
        if len(flagged) > 20:
            lines.append(f"- … and {len(flagged) - 20} more")
    lines += [
        "",
        "Redundant evidence can make a faithful answer look unchanged; these are leads, not verdicts.",
    ]
    return "\n".join(lines) + "\n"
