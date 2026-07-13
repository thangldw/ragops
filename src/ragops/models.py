from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Thresholds:
    citation_coverage: float
    lexical_groundedness: float
    max_latency_ms: int
    max_cost_usd: float
    citation_precision: float = 0.0


@dataclass(frozen=True)
class RedTeamPolicy:
    forbidden_output_terms: tuple[str, ...] = ()
    require_human_approval_for_external_actions: bool = True
    external_action_markers: tuple[str, ...] = ("sent email", "created ticket", "deleted")


@dataclass(frozen=True)
class EvalCase:
    id: str
    question: str
    evidence: tuple[str, ...]
    required_citation_ids: tuple[str, ...]
    category: str = "unspecified"
    severity: str = "medium"
    language: str = "und"
    tags: tuple[str, ...] = ()
    attack_category: str | None = None


@dataclass(frozen=True)
class Scenario:
    schema_version: str
    id: str
    name: str
    thresholds: Thresholds
    redteam: RedTeamPolicy
    cases: tuple[EvalCase, ...]


@dataclass(frozen=True)
class RecordedResponse:
    case_id: str
    answer: str
    citation_ids: tuple[str, ...]
    latency_ms: int
    cost_usd: float
    human_approved: bool = False
    retrieved_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AttackCase:
    id: str
    category: str
    input_text: str
    expected_rule: str
    severity: str
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class AttackPack:
    schema_version: str
    id: str
    name: str
    attacks: tuple[AttackCase, ...]


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    message: str


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    citation_coverage: float
    citation_precision: float
    lexical_groundedness: float
    latency_ms: int
    cost_usd: float
    findings: tuple[Finding, ...] = ()
    custom_metrics: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationReport:
    report_version: str
    scenario_id: str
    passed: bool
    metrics: dict[str, float]
    failed_gates: tuple[str, ...]
    cases: tuple[CaseResult, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RegressionPolicy:
    max_citation_coverage_drop: float = 0.0
    max_citation_precision_drop: float = 0.0
    max_groundedness_drop: float = 0.05
    max_latency_increase_ms: float = 250.0
    max_cost_increase_usd: float = 0.005


@dataclass(frozen=True)
class MetricGate:
    minimum: float | None = None
    maximum: float | None = None


@dataclass(frozen=True)
class EvaluationPolicy:
    metric_gates: dict[str, MetricGate] = field(default_factory=dict)
    fail_on_severity: str = "critical"


@dataclass(frozen=True)
class ComparisonReport:
    report_version: str
    scenario_id: str
    passed: bool
    baseline_passed: bool
    candidate_passed: bool
    deltas: dict[str, float]
    failed_gates: tuple[str, ...]
    baseline: EvaluationReport
    candidate: EvaluationReport

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
