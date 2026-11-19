"""Route evaluated cases by how far their score is from the threshold, using a calibration band.

A calibrated evaluator is only trustworthy away from its threshold. Cases clearly above or below
(by the margin measured against human labels) are decided automatically; the rest are queued for a
person. The report says how much was decided and the agreement with humans measured on that part.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ragops.calibration import ConfidenceBand
from ragops.loader import ContractError

ROUTES = ("auto-pass", "auto-fail", "needs-review")


@dataclass(frozen=True)
class TriagedCase:
    case_id: str
    score: float
    route: str


@dataclass(frozen=True)
class TriageReport:
    metric: str
    band: ConfidenceBand
    cases: tuple[TriagedCase, ...]

    def counts(self) -> dict[str, int]:
        return {route: sum(case.route == route for case in self.cases) for route in ROUTES}

    @property
    def decided_share(self) -> float:
        return 1 - self.counts()["needs-review"] / len(self.cases)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "band": asdict(self.band),
            "counts": self.counts(),
            "decided_share": self.decided_share,
            "cases": [asdict(case) for case in self.cases],
        }


def load_band(path: str | Path) -> ConfidenceBand:
    data = _read_json(path, "calibration report")
    raw = data.get("confidence_band") if isinstance(data, dict) else None
    if raw is None:
        raise ContractError(
            "The calibration report has no confidence band: it needs labeled records and a "
            "--target-accuracy the evaluator can reach"
        )
    try:
        return ConfidenceBand(**raw)
    except TypeError as exc:
        raise ContractError(f"Invalid confidence band: {exc}") from exc


def load_evaluation_scores(path: str | Path, metric: str) -> dict[str, float]:
    data = _read_json(path, "evaluation report")
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list) or not cases:
        raise ContractError("The evaluation report has no cases")
    scores: dict[str, float] = {}
    for index, case in enumerate(cases):
        if not isinstance(case, dict) or not isinstance(case.get("case_id"), str):
            raise ContractError(f"Evaluation case {index} has no case_id")
        value = case.get(metric)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ContractError(f"Evaluation case {case['case_id']!r} has no numeric {metric!r}")
        if case["case_id"] in scores:
            raise ContractError(f"Duplicate case_id {case['case_id']!r} in the evaluation report")
        scores[case["case_id"]] = float(value)
    return scores


def triage_cases(scores: dict[str, float], band: ConfidenceBand, metric: str) -> TriageReport:
    if not scores:
        raise ContractError("Nothing to triage")
    margin = band.margin
    routed = []
    for case_id, score in scores.items():
        distance = abs(score - band.threshold)
        if distance < margin:
            route = "needs-review"
        else:
            route = "auto-pass" if score >= band.threshold else "auto-fail"
        routed.append(TriagedCase(case_id, score, route))
    return TriageReport(metric, band, tuple(routed))


def triage_markdown(report: TriageReport) -> str:
    counts = report.counts()
    band = report.band
    lines = [
        f"## RAGOps triage on `{report.metric}`",
        "",
        f"Scores within the band ({band.lower:.4g}, {band.upper:.4g}) around the {band.threshold:.4g} "
        f"threshold are not trusted. On your human labels the evaluator agreed with people on "
        f"{band.accuracy:.0%} of the {band.decided_cases} cases outside the band ({band.coverage:.0%} of the labeled set).",
        "",
        f"- auto-pass: {counts['auto-pass']}",
        f"- auto-fail: {counts['auto-fail']}",
        f"- needs-review: {counts['needs-review']} ({1 - report.decided_share:.0%})",
        "",
    ]
    queue = [case for case in report.cases if case.route == "needs-review"]
    if queue:
        lines += ["| Needs review | Score |", "| --- | ---: |"]
        lines += [f"| `{case.case_id.replace('|', chr(92) + '|').replace('`', chr(92) + '`')}` | {case.score:.4g} |" for case in queue]
    return "\n".join(lines) + "\n"


def _read_json(path: str | Path, label: str) -> Any:
    try:
        return json.loads(
            Path(path).read_text(encoding="utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"non-finite JSON number {value}")),
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise ContractError(f"Cannot read {label} {path}: {exc}") from exc
