"""Gate semantics pinned down by mutation testing of policy_v2: boundaries, directions, tails, slices, waivers."""

from dataclasses import replace

import pytest

from ragops.loader import ContractError, scenario_from_dict
from ragops.models import CaseResult, EvaluationReport, Finding
from ragops.policy_v2 import (
    PolicyGate,
    PolicyWaiver,
    ReleasePolicyV2,
    SlicePolicy,
    TailGate,
    apply_release_policy,
)
from ragops.slices import SliceSelector

NOW = "2026-08-23T00:00:00Z"


def _scenario():
    return scenario_from_dict(
        {
            "schema_version": "0.2",
            "id": "s",
            "name": "S",
            "thresholds": {
                "citation_coverage": 0,
                "citation_precision": 0,
                "lexical_groundedness": 0,
                "max_latency_ms": 5000,
                "max_cost_usd": 1,
            },
            "cases": [
                {"id": "critical", "question": "Q?", "evidence": ["e"], "required_citation_ids": ["c1"],
                 "category": "policy", "severity": "critical", "language": "ja"},
                {"id": "routine", "question": "Q?", "evidence": ["e"], "required_citation_ids": ["c2"],
                 "category": "faq", "severity": "low", "language": "en"},
            ],
        }
    )


def _report(coverage=(1.0, 1.0), latencies=(100, 200), scenario_id="s", **extra):
    cases = (
        CaseResult("critical", coverage[0], 1.0, 1.0, latencies[0], 0.001),
        CaseResult("routine", coverage[1], 1.0, 1.0, latencies[1], 0.001),
    )
    metrics = {
        "citation_coverage": sum(coverage) / 2,
        "citation_precision": 1.0,
        "lexical_groundedness": 1.0,
        "avg_latency_ms": sum(latencies) / 2,
        "avg_cost_usd": 0.001,
        "critical_findings": 0.0,
    }
    metrics.update(extra)
    return EvaluationReport("0.1", scenario_id, True, metrics, (), cases)


def _policy(metrics=(), slices=(), tails=(), waivers=(), minimum_cases=1, insufficient="block"):
    return ReleasePolicyV2(minimum_cases, insufficient, tuple(metrics), tuple(slices), tuple(tails), tuple(waivers))


def _run(policy, baseline=None, candidate=None, now=NOW):
    return apply_release_policy(policy, baseline or _report(), candidate or _report(), _scenario(), now=now)


def _gate(decision, gate_id):
    return next(gate for gate in decision.gates if gate.id == gate_id)


def test_minimum_boundary_is_inclusive_and_exact_evidence_is_recorded() -> None:
    gate = PolicyGate("citation_coverage", "higher", minimum=0.9)
    at = _gate(_run(_policy([gate]), candidate=_report(coverage=(0.9, 0.9))), "global:citation_coverage:minimum")
    assert at.passed and (at.observed, at.threshold, at.comparator) == (0.9, 0.9, ">=")
    below = _run(_policy([gate]), candidate=_report(coverage=(0.8, 0.9)))
    failed = _gate(below, "global:citation_coverage:minimum")
    assert not failed.passed and failed.severity == "block" and failed.scope == "global"
    assert failed.metric == "citation_coverage" and failed.policy_path == "metrics.citation_coverage.minimum"
    assert failed.case_ids == ("critical", "routine") and failed.waived is False
    assert below.decision == "BLOCK" and below.passed is False


def test_maximum_boundary_is_inclusive() -> None:
    gate = PolicyGate("avg_latency_ms", "lower", maximum=150)
    at = _gate(_run(_policy([gate])), "global:avg_latency_ms:maximum")
    assert at.passed and at.comparator == "<=" and at.threshold == 150.0
    over = _gate(_run(_policy([gate]), candidate=_report(latencies=(100, 202))), "global:avg_latency_ms:maximum")
    assert not over.passed and over.observed == 151.0
    assert over.policy_path == "metrics.avg_latency_ms.maximum" and over.severity == "block"


def test_higher_is_better_regression_budget() -> None:
    gate = PolicyGate("citation_coverage", "higher", minimum=0.0, max_regression=0.25)
    ok = _gate(_run(_policy([gate]), candidate=_report(coverage=(0.5, 1.0))), "global:citation_coverage:regression")
    assert ok.passed and (ok.observed, ok.threshold, ok.comparator) == (-0.25, -0.25, ">=")
    bad = _gate(_run(_policy([gate]), candidate=_report(coverage=(0.4, 1.0))), "global:citation_coverage:regression")
    assert not bad.passed and bad.observed == pytest.approx(-0.3)
    assert bad.policy_path == "metrics.citation_coverage.max_regression"
    improved = _gate(_run(_policy([gate]), candidate=_report(coverage=(1.0, 1.0))), "global:citation_coverage:regression")
    assert improved.passed and improved.observed == 0.0


def test_lower_is_better_regression_budget() -> None:
    gate = PolicyGate("avg_latency_ms", "lower", maximum=10000, max_regression=50)
    baseline = _report(latencies=(100, 100))
    ok = _gate(_run(_policy([gate]), baseline, _report(latencies=(100, 200))), "global:avg_latency_ms:regression")
    assert ok.passed and (ok.observed, ok.threshold, ok.comparator) == (50.0, 50.0, "<=")
    bad = _gate(_run(_policy([gate]), baseline, _report(latencies=(100, 202))), "global:avg_latency_ms:regression")
    assert not bad.passed and bad.observed == 51.0
    faster = _gate(_run(_policy([gate]), baseline, _report(latencies=(50, 50))), "global:avg_latency_ms:regression")
    assert faster.passed and faster.observed == -50.0


def test_regression_gate_follows_the_absolute_gate() -> None:
    only_min = _run(_policy([PolicyGate("citation_coverage", "higher", minimum=0.5, max_regression=0.1)]))
    assert [g.id for g in only_min.gates] == ["global:citation_coverage:minimum", "global:citation_coverage:regression"]
    only_max = _run(_policy([PolicyGate("avg_latency_ms", "lower", maximum=500, max_regression=10)]))
    assert [g.id for g in only_max.gates] == ["global:avg_latency_ms:maximum", "global:avg_latency_ms:regression"]


def test_unavailable_metric_in_either_report_is_a_contract_error() -> None:
    gate = PolicyGate("custom_score", "higher", minimum=0.1)
    with_metric = _report(custom_score=0.5)
    with pytest.raises(ContractError, match="'custom_score' is unavailable"):
        _run(_policy([gate]), _report(), _report())
    with pytest.raises(ContractError, match="unavailable"):
        _run(_policy([gate]), with_metric, _report())
    with pytest.raises(ContractError, match="unavailable"):
        _run(_policy([gate]), _report(), with_metric)
    assert _run(_policy([gate]), with_metric, with_metric).decision == "PASS"


def test_minimum_case_count_and_scenario_mismatch() -> None:
    assert _run(_policy(minimum_cases=2)).decision == "PASS"
    with pytest.raises(ContractError, match="requires 3 cases; candidate has 2"):
        _run(_policy(minimum_cases=3))
    with pytest.raises(ContractError, match="scenario and reports must match"):
        _run(_policy(), baseline=_report(scenario_id="other"))
    with pytest.raises(ContractError, match="scenario and reports must match"):
        _run(_policy(), candidate=_report(scenario_id="other"))


def test_slice_with_too_few_cases_yields_one_evidence_gate_and_skips_its_metrics() -> None:
    metric = PolicyGate("citation_coverage", "higher", minimum=0.5)
    slices = (
        SlicePolicy(SliceSelector("ja", language="ja"), minimum_cases=2),
        SlicePolicy(SliceSelector("en", language="en"), minimum_cases=1),
    )
    decision = _run(_policy([metric], slices, insufficient="warn"))
    ids = [gate.id for gate in decision.gates]

    assert ids == ["global:citation_coverage:minimum", "slice:ja:minimum_cases", "slice:en:citation_coverage:minimum"]
    thin = _gate(decision, "slice:ja:minimum_cases")
    assert (thin.metric, thin.scope, thin.observed, thin.threshold, thin.comparator) == ("case_count", "ja", 1.0, 2.0, ">=")
    assert thin.passed is False and thin.severity == "warn" and thin.policy_path == "slices.ja.minimum_cases"
    assert thin.case_ids == ("critical",)
    assert decision.decision == "WARN"
    en = _gate(decision, "slice:en:citation_coverage:minimum")
    assert en.scope == "en" and en.case_ids == ("routine",)
    assert en.policy_path == "slices.en.metrics.citation_coverage.minimum" and en.passed


def test_slice_gates_see_only_that_slices_cases() -> None:
    metric = PolicyGate("citation_coverage", "higher", minimum=0.9)
    slices = (SlicePolicy(SliceSelector("ja", language="ja")),)
    decision = _run(_policy([metric], slices), candidate=_report(coverage=(0.5, 1.0)))
    assert _gate(decision, "global:citation_coverage:minimum").passed is False
    ja = _gate(decision, "slice:ja:citation_coverage:minimum")
    assert ja.observed == 0.5 and ja.passed is False


def test_tail_gates_use_the_candidate_quantile_and_inclusive_bounds() -> None:
    tails = (
        TailGate("latency_ms", 1.0, maximum=200),
        TailGate("citation_coverage", 0.5, minimum=0.75),
    )
    decision = _run(_policy(tails=tails), candidate=_report(coverage=(0.5, 1.0)))
    top = _gate(decision, "tail:latency_ms:p100:maximum")
    assert top.passed and top.observed == 200.0 and top.comparator == "<=" and top.scope == "global"
    assert top.policy_path == "tails.latency_ms.maximum" and top.case_ids == ("critical", "routine")
    mid = _gate(decision, "tail:citation_coverage:p50:minimum")
    assert mid.passed and mid.observed == 0.75 and mid.comparator == ">="
    assert mid.policy_path == "tails.citation_coverage.minimum"

    tight = _run(_policy(tails=(TailGate("latency_ms", 1.0, maximum=199), TailGate("citation_coverage", 0.5, minimum=0.76))),
                 candidate=_report(coverage=(0.5, 1.0)))
    assert not _gate(tight, "tail:latency_ms:p100:maximum").passed
    assert not _gate(tight, "tail:citation_coverage:p50:minimum").passed
    assert tight.decision == "BLOCK"


def test_tail_with_both_bounds_and_warn_severity() -> None:
    decision = _run(_policy(tails=(TailGate("latency_ms", 1.0, minimum=300, severity="warn"),)))
    assert decision.decision == "WARN" and decision.gates[0].severity == "warn"


def test_tail_metrics_can_be_standard_custom_or_unavailable() -> None:
    base = _report()
    with_custom = replace(base, cases=(replace(base.cases[0], custom_metrics={"tone": 0.4}), replace(base.cases[1], custom_metrics={"tone": 0.8})))
    gate = TailGate("tone", 1.0, minimum=0.8)
    assert _run(_policy(tails=(gate,)), candidate=with_custom).decision == "PASS"
    with pytest.raises(ContractError, match="Release tail metric 'tone' is unavailable"):
        _run(_policy(tails=(gate,)))
    finding = Finding("x", "low", "m")
    with_finding = replace(base, cases=(replace(base.cases[0], findings=(finding, finding)), base.cases[1]))
    assert _run(_policy(tails=(TailGate("finding_count", 1.0, maximum=2),)), candidate=with_finding).decision == "PASS"
    assert _run(_policy(tails=(TailGate("finding_count", 1.0, maximum=1),)), candidate=with_finding).decision == "BLOCK"
    assert _run(_policy(tails=(TailGate("cost_usd", 1.0, maximum=0.001),))).decision == "PASS"
    assert _run(_policy(tails=(TailGate("citation_precision", 0.01, minimum=1.0),))).decision == "PASS"
    assert _run(_policy(tails=(TailGate("lexical_groundedness", 0.01, minimum=1.0),))).decision == "PASS"


def test_decision_levels_and_serialisation() -> None:
    passing = _run(_policy([PolicyGate("citation_coverage", "higher", minimum=0.5)]))
    assert (passing.decision, passing.passed, passing.schema_version, passing.scenario_id) == ("PASS", True, "1.0", "s")
    warn = _run(_policy([PolicyGate("citation_coverage", "higher", minimum=1.1, severity="warn")]))
    assert warn.decision == "WARN" and warn.passed is False
    blocked = _run(_policy([PolicyGate("citation_coverage", "higher", minimum=1.1, severity="warn"),
                            PolicyGate("citation_precision", "higher", minimum=1.1)]))
    assert blocked.decision == "BLOCK"
    data = blocked.to_dict()
    assert set(data) == {"schema_version", "scenario_id", "decision", "passed", "gates"}
    assert data["passed"] is False and data["gates"][0]["id"] == "global:citation_coverage:minimum"


def _waiver(**overrides):
    values = dict(gate_id="global:citation_coverage:minimum", owner="o", reason="r",
                  issued_at="2026-08-01T00:00:00Z", expires_at="2026-09-01T00:00:00Z")
    values.update(overrides)
    return PolicyWaiver(**values)


def _failing(waiver):
    gate = PolicyGate("citation_coverage", "higher", minimum=0.9)
    return _run(_policy([gate], waivers=[waiver]), candidate=_report(coverage=(0.5, 0.5)))


def test_waiver_window_is_inclusive_at_issue_and_exclusive_at_expiry() -> None:
    assert _failing(_waiver(issued_at=NOW)).gates[0].waived is True
    assert _failing(_waiver(expires_at=NOW)).gates[0].waived is False
    assert _failing(_waiver(issued_at="2026-08-23T00:00:01Z")).gates[0].waived is False
    active = _failing(_waiver()).gates[0]
    assert (active.waiver_owner, active.waiver_reason, active.waiver_expires_at) == ("o", "r", "2026-09-01T00:00:00Z")
    assert _failing(_waiver()).decision == "WARN"


def test_waiver_must_match_gate_id_and_scope() -> None:
    assert _failing(_waiver(gate_id="global:other:minimum")).gates[0].waived is False
    assert _failing(_waiver(scope="global")).gates[0].waived is True
    assert _failing(_waiver(scope="ja")).gates[0].waived is False


def test_a_second_matching_waiver_applies_when_the_first_has_expired() -> None:
    gate = PolicyGate("citation_coverage", "higher", minimum=0.9)
    waivers = [_waiver(expires_at="2026-08-02T00:00:00Z"), _waiver(owner="second", scope="global")]
    decision = _run(_policy([gate], waivers=waivers), candidate=_report(coverage=(0.5, 0.5)))
    assert decision.gates[0].waived and decision.gates[0].waiver_owner == "second"


def test_passing_gates_are_never_marked_waived() -> None:
    gate = PolicyGate("citation_coverage", "higher", minimum=0.5)
    decision = _run(_policy([gate], waivers=[_waiver()]))
    assert decision.gates[0].passed and decision.gates[0].waived is False and decision.decision == "PASS"


@pytest.mark.parametrize(
    "now,message",
    [("not-a-date", "ISO-8601"), ("2026-08-23T00:00:00", "must include a timezone"), (None, "ISO-8601")],
)
def test_evaluation_time_must_be_a_timezone_aware_timestamp(now, message) -> None:
    with pytest.raises(ContractError, match=message):
        _run(_policy(), now=now)
    with pytest.raises(ContractError, match="policy evaluation time"):
        _run(_policy(), now=now)


def test_waiver_timestamps_are_validated_with_their_labels() -> None:
    with pytest.raises(ContractError):
        _failing(_waiver(issued_at="bad"))


def test_maximum_regression_and_tail_gates_carry_full_evidence_fields() -> None:
    slices = (SlicePolicy(SliceSelector("ja", language="ja")),)
    metric = PolicyGate("citation_coverage", "higher", maximum=0.1, max_regression=0, severity="warn")
    decision = _run(_policy([metric], slices, tails=(TailGate("latency_ms", 1.0, maximum=1, severity="warn"),)))
    for gate_id in ("global:citation_coverage:maximum", "slice:ja:citation_coverage:maximum"):
        gate = _gate(decision, gate_id)
        scope = "global" if gate_id.startswith("global") else "ja"
        cases = ("critical", "routine") if scope == "global" else ("critical",)
        assert (gate.metric, gate.scope, gate.severity, gate.case_ids) == ("citation_coverage", scope, "warn", cases)
    reg = _gate(decision, "slice:ja:citation_coverage:regression")
    assert (reg.metric, reg.scope, reg.severity, reg.case_ids) == ("citation_coverage", "ja", "warn", ("critical",))
    tail = _gate(decision, "tail:latency_ms:p100:maximum")
    assert (tail.metric, tail.scope, tail.severity, tail.case_ids) == ("latency_ms", "global", "warn", ("critical", "routine"))


def test_tail_minimum_gate_carries_metric_scope_and_cases() -> None:
    decision = _run(_policy(tails=(TailGate("citation_coverage", 0.5, minimum=0.5),)))
    gate = _gate(decision, "tail:citation_coverage:p50:minimum")
    assert (gate.metric, gate.scope, gate.case_ids) == ("citation_coverage", "global", ("critical", "routine"))


@pytest.mark.parametrize(
    "policy,message",
    [
        (_policy(minimum_cases=0), "minimum_cases must be a positive integer"),
        (_policy(minimum_cases=True), "minimum_cases must be a positive integer"),
        (_policy(minimum_cases=1.5), "minimum_cases must be a positive integer"),
        (_policy(insufficient="maybe"), "insufficient_evidence must be warn or block"),
        (_policy([PolicyGate("m", "higher", minimum=1), PolicyGate("m", "higher", minimum=1)]), "unique"),
        (_policy([PolicyGate("", "higher", minimum=1)]), "non-empty and unique"),
        (_policy([PolicyGate("m", "sideways", minimum=1)]), "direction must be higher or lower"),
        (_policy([PolicyGate("m", "higher")]), "exactly one absolute threshold"),
        (_policy([PolicyGate("m", "higher", minimum=1, maximum=2)]), "exactly one absolute threshold"),
        (_policy([PolicyGate("m", "higher", minimum=1, max_regression=-0.1)]), "max_regression must be non-negative"),
        (_policy([PolicyGate("m", "higher", minimum=float("nan"))]), "m"),
        (_policy([PolicyGate("m", "higher", minimum=1, severity="fatal")]), "severity must be warn or block"),
        (_policy(slices=[SlicePolicy(SliceSelector("a", language="ja")), SlicePolicy(SliceSelector("a", language="en"))]), "unique"),
        (_policy(slices=[SlicePolicy(SliceSelector("", language="ja"))]), "non-empty and unique"),
        (_policy(slices=[SlicePolicy(SliceSelector("a"))]), "must select at least one field"),
        (_policy(slices=[SlicePolicy(SliceSelector("a", language="ja"), minimum_cases=0)]), "minimum_cases must be positive"),
        (_policy(slices=[SlicePolicy(SliceSelector("a", language="ja"), minimum_cases=True)]), "minimum_cases must be positive"),
        (_policy(tails=[TailGate("", 0.5, minimum=1)]), "tail metric must be non-empty"),
        (_policy(tails=[TailGate("m", 0.0, minimum=1)]), r"percentile must be in \(0, 1\]"),
        (_policy(tails=[TailGate("m", 1.5, minimum=1)]), r"percentile must be in \(0, 1\]"),
        (_policy(tails=[TailGate("m", 0.5)]), "must define one threshold"),
        (_policy(tails=[TailGate("m", 0.5, minimum=1, maximum=2)]), "must define one threshold"),
        (_policy(tails=[TailGate("m", 0.5, minimum=1, severity="fatal")]), "severity must be warn or block"),
        (_policy(waivers=[_waiver(), _waiver()]), "unique gate_id and scope"),
        (_policy(waivers=[_waiver(owner="")]), "must be non-empty"),
        (_policy(waivers=[_waiver(reason="")]), "must be non-empty"),
        (_policy(waivers=[_waiver(gate_id="")]), "must be non-empty"),
        (_policy(waivers=[_waiver(expires_at="2026-08-01T00:00:00Z")]), "must expire after issuance"),
        (_policy(waivers=[_waiver(issued_at="nope")]), "issued_at"),
        (_policy(waivers=[_waiver(expires_at="nope")]), "expires_at"),
    ],
)
def test_invalid_policies_are_rejected_with_a_specific_message(policy, message) -> None:
    with pytest.raises(ContractError, match=message):
        _run(policy)
