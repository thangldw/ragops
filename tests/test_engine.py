from dataclasses import replace

from ragops.engine import evaluate
from ragops.loader import load_responses, load_scenario

SCENARIO = "scenarios/japanese_troubleshooting/scenario.json"
RESPONSES = "scenarios/japanese_troubleshooting/sample_responses.json"


def test_sample_scenario_passes_release_gate() -> None:
    report = evaluate(load_scenario(SCENARIO), load_responses(RESPONSES))

    assert report.passed is True
    assert report.failed_gates == ()
    assert report.metrics["citation_coverage"] == 1.0
    assert report.metrics["critical_findings"] == 0


def test_secret_leak_blocks_release() -> None:
    scenario = load_scenario(SCENARIO)
    responses = list(load_responses(RESPONSES))
    responses[0] = replace(responses[0], answer=responses[0].answer + " FPT_INTERNAL_SECRET_42")

    report = evaluate(scenario, tuple(responses))

    assert report.passed is False
    assert "critical_redteam_finding" in report.failed_gates
    assert report.cases[0].findings[0].rule == "forbidden_output_term"


def test_external_action_requires_human_approval() -> None:
    scenario = load_scenario(SCENARIO)
    responses = list(load_responses(RESPONSES))
    responses[0] = replace(responses[0], answer="I created ticket INC-42")

    report = evaluate(scenario, tuple(responses))

    rules = {finding.rule for finding in report.cases[0].findings}
    assert "external_action_without_approval" in rules

