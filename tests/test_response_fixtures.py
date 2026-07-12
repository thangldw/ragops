import json

import pytest

from ragops.engine import compare, evaluate
from ragops.loader import ContractError, load_responses, load_scenario

SCENARIO = "scenarios/japanese_troubleshooting/benchmark-v0.2.json"
BASELINE = "scenarios/japanese_troubleshooting/benchmark-baseline.json"
REGRESSED = "scenarios/japanese_troubleshooting/benchmark-regressed.json"
ADVERSARIAL = "scenarios/japanese_troubleshooting/benchmark-adversarial.json"


def test_regressed_overlay_blocks_quality_and_budget_gates() -> None:
    report = compare(
        load_scenario(SCENARIO),
        load_responses(BASELINE),
        load_responses(REGRESSED),
    )

    assert report.passed is False
    assert "citation_coverage_regression" in report.failed_gates
    assert "citation_precision_regression" in report.failed_gates
    assert "groundedness_regression" in report.failed_gates
    assert "latency_regression" in report.failed_gates
    assert "cost_regression" in report.failed_gates


def test_adversarial_overlay_blocks_critical_findings() -> None:
    report = evaluate(load_scenario(SCENARIO), load_responses(ADVERSARIAL))
    rules = {finding.rule for case in report.cases for finding in case.findings}

    assert report.passed is False
    assert report.metrics["critical_findings"] == 5.0
    assert rules == {"forbidden_output_term", "external_action_without_approval"}


def test_overlay_rejects_unknown_case(tmp_path) -> None:
    baseline = tmp_path / "base.json"
    baseline.write_text(
        '[{"case_id":"q1","answer":"a","citation_ids":[],"latency_ms":1,"cost_usd":0}]',
        encoding="utf-8",
    )
    overlay = tmp_path / "overlay.json"
    overlay.write_text(
        json.dumps(
            {
                "schema_version": "0.2",
                "extends": "base.json",
                "overrides": [{"case_id": "unknown", "answer": "x"}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ContractError, match="unknown override"):
        load_responses(overlay)


def test_overlay_rejects_cycle(tmp_path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(
        '{"schema_version":"0.2","extends":"second.json","overrides":[]}',
        encoding="utf-8",
    )
    second.write_text(
        '{"schema_version":"0.2","extends":"first.json","overrides":[]}',
        encoding="utf-8",
    )

    with pytest.raises(ContractError, match="cycle"):
        load_responses(first)
