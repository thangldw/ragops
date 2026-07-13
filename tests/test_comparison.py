from ragops.engine import compare
from ragops.loader import load_responses, load_scenario
from ragops.models import EvaluationPolicy, MetricGate
from ragops.plugins import ClaimSupportEvaluator
from ragops.reporters import comparison_markdown

SCENARIO = "scenarios/japanese_troubleshooting/scenario.json"
BASELINE = "scenarios/japanese_troubleshooting/sample_responses.json"
REGRESSED = "scenarios/japanese_troubleshooting/regressed_responses.json"


def test_identical_candidate_has_no_regressions() -> None:
    scenario = load_scenario(SCENARIO)
    responses = load_responses(BASELINE)

    report = compare(scenario, responses, responses)

    assert report.passed is True
    assert report.failed_gates == ()
    assert set(report.deltas.values()) == {0.0}


def test_regressed_candidate_is_blocked() -> None:
    report = compare(
        load_scenario(SCENARIO),
        load_responses(BASELINE),
        load_responses(REGRESSED),
    )

    assert report.passed is False
    assert "candidate_release_gate" in report.failed_gates
    assert "citation_coverage_regression" in report.failed_gates
    assert "new_critical_findings" in report.failed_gates


def test_markdown_report_is_pr_ready() -> None:
    scenario = load_scenario(SCENARIO)
    responses = load_responses(BASELINE)

    rendered = comparison_markdown(compare(scenario, responses, responses))

    assert rendered.startswith("# RAGOps regression check: PASS")
    assert "| Metric | Baseline | Candidate | Delta |" in rendered
    assert "None." in rendered


def test_compare_uses_same_plugin_gate_and_reports_custom_deltas() -> None:
    report = compare(
        load_scenario(SCENARIO),
        load_responses(BASELINE),
        load_responses(REGRESSED),
        evaluators=(ClaimSupportEvaluator(),),
        evaluation_policy=EvaluationPolicy(
            metric_gates={"claim_support": MetricGate(minimum=0.95)}
        ),
    )

    assert "claim_support" in report.deltas
    assert "claim_support.score" in report.deltas
    assert report.candidate.failed_gates.count("metric_minimum:claim_support") == 1
    assert "candidate_release_gate" in report.failed_gates
