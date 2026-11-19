"""``ragops init``: turn real RAG logs into a first release-gate scenario.

The logs are read as generic JSON/JSONL records. Field names are inferred from a
small alias table, so a typical export works without a schema. The generated
scenario is a *snapshot baseline*: thresholds sit just below today's measured
behaviour, so it detects regressions from now on. It does not claim today's
answers are correct.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ragops.adapters.trace_import import convert_traces
from ragops.engine import compare, evaluate
from ragops.loader import ContractError, load_responses, load_scenario
from ragops.plugins import StrictGroundingEvaluator
from ragops.reporters import comparison_markdown, evaluation_markdown

MAX_FILE_BYTES = 64 * 1024 * 1024
ALIASES: dict[str, tuple[str, ...]] = {
    "id": ("case_id", "id", "trace_id", "run_id", "request_id"),
    "question": ("question", "query", "prompt", "input.question", "input.query", "input"),
    "answer": ("answer", "output.answer", "output.text", "response", "output", "completion"),
    "contexts": (
        "contexts", "retrieved_contexts", "evidence", "documents", "retrieval.contexts",
        "retrieval.documents", "context", "sources",
    ),
    "citations": ("citation_ids", "citations", "output.citation_ids", "cited_ids"),
    "latency": ("latency_ms", "latency", "duration_ms", "usage.latency_ms"),
    "cost": ("cost_usd", "cost", "usage.cost_usd", "usage.cost"),
}
TEXT_KEYS = ("text", "content", "page_content", "snippet", "body")
ID_KEYS = ("id", "doc_id", "document_id", "source_id", "chunk_id")


@dataclass
class InitResult:
    cases: int
    skipped: Counter[str] = field(default_factory=Counter)
    files: list[str] = field(default_factory=list)
    passed: bool = True
    failed_gates: tuple[str, ...] = ()
    metrics: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "cases": self.cases,
            "skipped": dict(self.skipped),
            "files": self.files,
            "first_run": {
                "passed": self.passed,
                "failed_gates": list(self.failed_gates),
                "metrics": self.metrics,
            },
            "notes": self.notes,
        }


def init_project(
    source: str | Path,
    output: str | Path,
    *,
    scenario_id: str = "my-rag",
    source_format: str = "generic",
    candidate: str | Path | None = None,
) -> InitResult:
    """Build ``scenario.json`` and ``responses.json`` from ``source`` logs.

    With ``candidate`` logs (a later run of the same questions) also write ``candidate.json`` and a
    baseline-versus-candidate comparison. Candidate answers are matched to baseline cases by id, else by
    normalized question, and are judged against the baseline case's evidence.
    """
    records = list(_read_records(Path(source)))
    if source_format != "generic":
        records = convert_traces(source_format, _unwrap(records))
    if not records:
        raise ContractError(f"No JSON or JSONL records found in {source}")
    result = InitResult(cases=0)
    cases: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    used: set[str] = set()
    for index, record in enumerate(records, start=1):
        normalized, reason = _normalize(record, index, used)
        if normalized is None:
            result.skipped[reason] += 1
            continue
        case, response = normalized
        cases.append(case)
        responses.append(response)
    if not cases:
        raise ContractError(
            "No usable records. Each needs a question, an answer and retrieved contexts. "
            f"Skipped: {dict(result.skipped)}. Fields seen in the first record: "
            f"{sorted(records[0]) if isinstance(records[0], dict) else type(records[0]).__name__}"
        )
    candidate_responses: list[dict[str, Any]] = []
    if candidate is not None:
        cases, responses, candidate_responses = _match_candidate(
            cases, responses, candidate, source_format, result
        )
    scenario = {
        "schema_version": "0.2",
        "id": scenario_id,
        "name": f"{scenario_id} release gate (snapshot baseline)",
        "thresholds": _thresholds(responses),
        "redteam": {"forbidden_output_terms": [], "require_human_approval_for_external_actions": True},
        "cases": cases,
    }
    root = Path(output)
    root.mkdir(parents=True, exist_ok=True)
    scenario_path, responses_path = root / "scenario.json", root / "responses.json"
    for path in (scenario_path, responses_path):
        if path.exists():
            raise ContractError(f"Refusing to overwrite {path}")
    scenario_path.write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    responses_path.write_text(json.dumps(responses, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    loaded = load_scenario(scenario_path)
    report = evaluate(loaded, load_responses(responses_path), evaluators=(StrictGroundingEvaluator(),))
    report_path = root / "first-report.md"
    report_path.write_text(evaluation_markdown(report).rstrip() + "\n", encoding="utf-8")
    result.cases = len(cases)
    result.files = [str(scenario_path), str(responses_path), str(report_path)]
    result.passed, result.failed_gates = report.passed, report.failed_gates
    result.metrics = report.metrics
    result.notes = [
        "Latency and cost limits are derived from your logs (p95 x 1.25, max x 1.25); quality thresholds are conservative defaults. Tune them in scenario.json.",
        "A failing first run usually means real unsupported answers in your logs: read first-report.md before changing thresholds.",
        "required_citation_ids were taken from the citations in your logs; review them.",
        "Findings on this first run (strict_grounding) are leads to read, not verdicts.",
    ]
    if candidate is not None:
        candidate_path, compare_path = root / "candidate.json", root / "compare-report.md"
        for path in (candidate_path, compare_path):
            if path.exists():
                raise ContractError(f"Refusing to overwrite {path}")
        candidate_path.write_text(
            json.dumps(candidate_responses, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        comparison = compare(
            loaded,
            load_responses(responses_path),
            load_responses(candidate_path),
            evaluators=(StrictGroundingEvaluator(),),
        )
        compare_path.write_text(comparison_markdown(comparison).rstrip() + "\n", encoding="utf-8")
        result.files += [str(candidate_path), str(compare_path)]
        result.notes.append(
            f"Compared {len(cases)} matched cases; candidate answers are judged against the baseline's evidence."
        )
        result.passed, result.failed_gates = comparison.passed, comparison.failed_gates
        result.metrics = {**comparison.candidate.metrics}
    return result


def _question_key(question: str) -> str:
    return " ".join(question.casefold().split())


def _match_candidate(
    cases: list[dict[str, Any]],
    responses: list[dict[str, Any]],
    candidate: str | Path,
    source_format: str,
    result: InitResult,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    records = list(_read_records(Path(candidate)))
    if source_format != "generic":
        records = convert_traces(source_format, _unwrap(records))
    by_id = {case["id"]: case for case in cases}
    by_question = {_question_key(case["question"]): case for case in cases}
    matched: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            result.skipped["candidate record is not an object"] += 1
            continue
        raw_id = _get(record, "id")
        question, answer = _text(_get(record, "question")), _text(_get(record, "answer"))
        case = by_id.get(str(raw_id)) if raw_id is not None else None
        if case is None and question:
            case = by_question.get(_question_key(question))
        if case is None:
            result.skipped["candidate has no matching baseline case"] += 1
            continue
        if not answer:
            result.skipped["candidate missing answer"] += 1
            continue
        if case["id"] in matched:
            result.skipped["candidate duplicates a case"] += 1
            continue
        citations = _get(record, "citations")
        cited = (
            [str(c.get("id", c)) if isinstance(c, dict) else str(c) for c in citations]
            if isinstance(citations, list)
            else []
        )
        matched[case["id"]] = {
            "case_id": case["id"],
            "answer": answer,
            "citation_ids": cited,
            "retrieved_ids": [],
            "latency_ms": int(_number(_get(record, "latency"), 0.0)),
            "cost_usd": _number(_get(record, "cost"), 0.0),
        }
    if not matched:
        raise ContractError(
            "No candidate record matched a baseline case (matching uses the case id, then the question text)"
        )
    kept_cases = [case for case in cases if case["id"] in matched]
    kept_responses = [response for response in responses if response["case_id"] in matched]
    dropped = len(cases) - len(kept_cases)
    if dropped:
        result.skipped["baseline case without a candidate answer"] += dropped
    return kept_cases, kept_responses, [matched[case["id"]] for case in kept_cases]


def _read_records(source: Path) -> Iterable[Any]:
    if source.is_symlink():
        raise ContractError(f"Refusing symlink input: {source}")
    files = (
        sorted(p for p in source.iterdir() if p.suffix in {".json", ".jsonl"} and not p.is_symlink())
        if source.is_dir()
        else [source]
    )
    for path in files:
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                raise ContractError(f"{path} is larger than {MAX_FILE_BYTES} bytes")
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise ContractError(f"Cannot read {path}: {exc}") from exc
        try:
            if path.suffix == ".jsonl":
                yield from (json.loads(line) for line in text.splitlines() if line.strip())
            else:
                data = json.loads(text)
                yield from data if isinstance(data, list) else [data]
        except json.JSONDecodeError as exc:
            raise ContractError(f"{path} is not valid JSON: {exc}") from exc


def _unwrap(records: list[Any]) -> list[Any]:
    """Accept API envelopes such as {"data": [...]} around the real records."""
    if len(records) == 1 and isinstance(records[0], dict):
        for key in ("data", "traces", "logs", "records"):
            if isinstance(records[0].get(key), list):
                return records[0][key]
    return records


def _get(record: dict[str, Any], key: str) -> Any:
    for alias in ALIASES[key]:
        node: Any = record
        for part in alias.split("."):
            node = node.get(part) if isinstance(node, dict) else None
            if node is None:
                break
        if node not in (None, "", []):
            return node
    return None


def _text(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        for key in ("text", "content", "answer", "question"):
            if isinstance(value.get(key), str) and value[key].strip():
                return value[key].strip()
    if isinstance(value, list) and value and all(isinstance(m, dict) for m in value):
        # chat-style message list: take the last user/assistant text
        for message in reversed(value):
            if isinstance(message.get("content"), str) and message["content"].strip():
                return message["content"].strip()
    return None


def _context(item: Any, position: int) -> tuple[str, str] | None:
    if isinstance(item, str):
        return (item.strip(), f"ctx-{position}") if item.strip() else None
    if isinstance(item, dict):
        text = next((item[k] for k in TEXT_KEYS if isinstance(item.get(k), str) and item[k].strip()), None)
        if text is None:
            return None
        identifier = next((str(item[k]) for k in ID_KEYS if item.get(k) not in (None, "")), None)
        if identifier is None and isinstance(item.get("metadata"), dict):
            identifier = next((str(item["metadata"][k]) for k in ID_KEYS if item["metadata"].get(k)), None)
        return text.strip(), identifier or f"ctx-{position}"
    return None


def _number(value: Any, default: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        return default
    return float(value)


def _normalize(record: Any, index: int, used: set[str]):
    if not isinstance(record, dict):
        return None, "record is not an object"
    question, answer = _text(_get(record, "question")), _text(_get(record, "answer"))
    raw_contexts = _get(record, "contexts")
    if not question:
        return None, "missing question"
    if not answer:
        return None, "missing answer"
    if not isinstance(raw_contexts, list):
        return None, "missing retrieved contexts"
    contexts = [c for n, item in enumerate(raw_contexts, 1) if (c := _context(item, n))]
    if not contexts:
        return None, "contexts have no text"
    raw_id = _get(record, "id")
    case_id = str(raw_id) if isinstance(raw_id, (str, int)) and str(raw_id).strip() else f"case-{index:04d}"
    while case_id in used:
        case_id += f"-{index}"
    used.add(case_id)
    citations = _get(record, "citations")
    cited = [str(c.get("id", c)) if isinstance(c, dict) else str(c) for c in citations] if isinstance(citations, list) else []
    context_ids = [identifier for _, identifier in contexts]
    case = {
        "id": case_id,
        "question": question,
        "evidence": [text for text, _ in contexts],
        "required_citation_ids": sorted(set(cited) & set(context_ids)) or sorted(set(cited)),
        "category": "imported",
        "severity": "medium",
    }
    response = {
        "case_id": case_id,
        "answer": answer,
        "citation_ids": cited,
        "retrieved_ids": context_ids,
        "latency_ms": int(_number(_get(record, "latency"), 0.0)),
        "cost_usd": _number(_get(record, "cost"), 0.0),
    }
    return (case, response), ""


def _thresholds(responses: list[dict[str, Any]]) -> dict[str, float]:
    latencies = sorted(r["latency_ms"] for r in responses)
    p95 = latencies[min(len(latencies) - 1, math.ceil(0.95 * len(latencies)) - 1)]
    cost = max(r["cost_usd"] for r in responses)
    return {
        "citation_coverage": 0.0 if not any(r["citation_ids"] for r in responses) else 0.9,
        "citation_precision": 0.0,
        "lexical_groundedness": 0.6,
        "max_latency_ms": int(math.ceil(max(p95 * 1.25, 1000) / 100) * 100),
        "max_cost_usd": round(cost * 1.25, 6),
    }
