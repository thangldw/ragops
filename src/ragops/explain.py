from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from ragops.policy_v2 import ReleaseDecision


@dataclass(frozen=True)
class GateExplanation:
    gate_id: str
    policy_path: str
    scope: str
    case_ids: tuple[str, ...]
    observed: float
    threshold: float
    comparator: str
    required_change: float
    waived: bool
    waiver: dict[str, str | None] | None
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DecisionExplanation:
    schema_version: str
    scenario_id: str
    decision: str
    items: tuple[GateExplanation, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "scenario_id": self.scenario_id,
            "decision": self.decision,
            "items": [item.to_dict() for item in self.items],
        }


_METRIC_NAMES = {
    "citation_coverage": "share of answers that cite a source",
    "citation_precision": "share of citations that point to relevant evidence",
    "lexical_groundedness": "share of answer words found in the evidence",
    "avg_latency_ms": "average response time (ms)",
    "latency_ms": "response time (ms)",
    "avg_cost_usd": "average cost per answer (USD)",
    "cost_usd": "cost per answer (USD)",
    "critical_findings": "number of critical findings",
    "case_count": "number of test cases",
}


def plain_reason(gate_id: str, metric: str, scope: str, observed: float, threshold: float, comparator: str) -> str:
    """One plain-language sentence saying why a gate failed."""
    name = _METRIC_NAMES.get(metric, metric.replace("_", " "))
    lead = "Overall, the" if scope == "global" else f"For the {scope} slice, the"
    kind = gate_id.rsplit(":", 1)[-1]
    if kind == "minimum_cases":
        return (
            f"The {scope} slice has only {observed:.0f} test cases but at least {threshold:.0f} are needed, "
            "so its result is not trustworthy yet. Add cases or lower the minimum."
        )
    if kind == "regression":
        worse = "dropped" if comparator == ">=" else "rose"
        allowed = abs(threshold)
        return (
            f"{lead} {name} {worse} by {abs(observed):.4g} compared with the baseline; "
            f"the policy allows at most {allowed:.4g}."
        )
    if comparator == ">=":
        return f"{lead} {name} is {observed:.4g}, below the required minimum of {threshold:.4g}."
    return f"{lead} {name} is {observed:.4g}, above the allowed maximum of {threshold:.4g}."


def explain_decision(decision: ReleaseDecision) -> DecisionExplanation:
    items = []
    for gate in decision.gates:
        if gate.passed:
            continue
        required_change = (
            max(0.0, gate.threshold - gate.observed)
            if gate.comparator == ">="
            else max(0.0, gate.observed - gate.threshold)
        )
        waiver = None
        if gate.waived:
            waiver = {
                "owner": gate.waiver_owner,
                "reason": gate.waiver_reason,
                "expires_at": gate.waiver_expires_at,
            }
        items.append(
            GateExplanation(
                gate_id=gate.id,
                policy_path=gate.policy_path,
                scope=gate.scope,
                case_ids=gate.case_ids,
                observed=gate.observed,
                threshold=gate.threshold,
                comparator=gate.comparator,
                required_change=required_change,
                waived=gate.waived,
                waiver=waiver,
                summary=plain_reason(gate.id, gate.metric, gate.scope, gate.observed, gate.threshold, gate.comparator),
            )
        )
    return DecisionExplanation("1.0", decision.scenario_id, decision.decision, tuple(items))
