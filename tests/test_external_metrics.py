import json
from pathlib import Path

import pytest

from ragops.adapters.external_metrics import (
    external_metric_envelope_from_dict,
    load_external_metric_evaluator,
    validate_external_metric_pair,
)
from ragops.cli import main
from ragops.engine import compare, evaluate
from ragops.loader import ContractError, load_responses, load_scenario
from ragops.models import EvaluationPolicy, MetricGate

SCENARIO_PATH = "scenarios/japanese_troubleshooting/scenario.json"
RESPONSES_PATH = "scenarios/japanese_troubleshooting/sample_responses.json"


def _write_envelope(
    path: Path,
    values: dict[str, float],
    provider: str = "ragas",
    metric_name: str = "faithfulness",
) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "provider": provider,
                "records": [
                    {"case_id": case_id, "metrics": {metric_name: value}}
                    for case_id, value in values.items()
                ],
            }
        ),
        encoding="utf-8",
    )


def test_external_metric_can_gate_evaluation(tmp_path: Path) -> None:
    scenario = load_scenario(SCENARIO_PATH)
    path = tmp_path / "ragas.json"
    _write_envelope(path, {case.id: 0.8 for case in scenario.cases})

    report = evaluate(
        scenario,
        load_responses(RESPONSES_PATH),
        evaluators=(load_external_metric_evaluator(path, scenario),),
        policy=EvaluationPolicy(
            metric_gates={"ragas.faithfulness": MetricGate(minimum=0.9)}
        ),
    )

    assert report.metrics["ragas.faithfulness"] == pytest.approx(0.8)
    assert report.passed is False
    assert report.failed_gates == ("metric_minimum:ragas.faithfulness",)


def test_compare_uses_distinct_compatible_external_envelopes(tmp_path: Path) -> None:
    scenario = load_scenario(SCENARIO_PATH)
    responses = load_responses(RESPONSES_PATH)
    baseline_path = tmp_path / "baseline.json"
    candidate_path = tmp_path / "candidate.json"
    _write_envelope(baseline_path, {case.id: 1.0 for case in scenario.cases})
    _write_envelope(candidate_path, {case.id: 0.8 for case in scenario.cases})
    baseline = load_external_metric_evaluator(baseline_path, scenario)
    candidate = load_external_metric_evaluator(candidate_path, scenario)
    validate_external_metric_pair(baseline, candidate)

    report = compare(
        scenario,
        responses,
        responses,
        baseline_evaluators=(baseline,),
        candidate_evaluators=(candidate,),
        evaluation_policy=EvaluationPolicy(
            metric_gates={"ragas.faithfulness": MetricGate(minimum=0.9)}
        ),
    )

    assert report.deltas["ragas.faithfulness"] == pytest.approx(-0.2)
    assert "candidate_release_gate" in report.failed_gates


def test_external_metric_coverage_fails_closed(tmp_path: Path) -> None:
    scenario = load_scenario(SCENARIO_PATH)
    path = tmp_path / "partial.json"
    _write_envelope(path, {scenario.cases[0].id: 1.0})

    with pytest.raises(ContractError, match="coverage mismatch"):
        load_external_metric_evaluator(path, scenario)


@pytest.mark.parametrize("value", [True, float("nan"), float("inf"), "high"])
def test_external_metrics_reject_invalid_numbers(value: object) -> None:
    data = {
        "schema_version": "0.1",
        "provider": "deepeval",
        "records": [{"case_id": "q1", "metrics": {"faithfulness": value}}],
    }

    with pytest.raises(ContractError):
        external_metric_envelope_from_dict(data)


def test_external_metrics_reject_unknown_fields() -> None:
    data = {
        "schema_version": "0.1",
        "provider": "langfuse",
        "records": [{"case_id": "q1", "metrics": {"score": 1.0}, "silent": True}],
    }

    with pytest.raises(ContractError, match="unknown fields"):
        external_metric_envelope_from_dict(data)


def test_external_metric_pair_rejects_provider_or_metric_mismatch(tmp_path: Path) -> None:
    scenario = load_scenario(SCENARIO_PATH)
    case_values = {case.id: 1.0 for case in scenario.cases}
    baseline_path = tmp_path / "baseline.json"
    candidate_path = tmp_path / "candidate.json"
    _write_envelope(baseline_path, case_values, provider="ragas")
    _write_envelope(candidate_path, case_values, provider="langfuse")
    baseline = load_external_metric_evaluator(baseline_path, scenario)
    candidate = load_external_metric_evaluator(candidate_path, scenario)

    with pytest.raises(ContractError, match="providers differ"):
        validate_external_metric_pair(baseline, candidate)

    _write_envelope(
        candidate_path,
        case_values,
        provider="ragas",
        metric_name="answer_relevance",
    )
    changed = load_external_metric_evaluator(candidate_path, scenario)
    with pytest.raises(ContractError, match="metric names differ"):
        validate_external_metric_pair(baseline, changed)


def test_compare_cli_applies_distinct_external_envelopes(monkeypatch, tmp_path: Path) -> None:
    output = tmp_path / "comparison.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "compare",
            "--scenario",
            SCENARIO_PATH,
            "--baseline",
            RESPONSES_PATH,
            "--candidate",
            RESPONSES_PATH,
            "--baseline-external-metrics",
            "scenarios/japanese_troubleshooting/external-metrics-baseline.json",
            "--candidate-external-metrics",
            "scenarios/japanese_troubleshooting/external-metrics-candidate.json",
            "--evaluation-policy",
            "scenarios/japanese_troubleshooting/external-metric-policy.toml",
            "--format",
            "json",
            "--output",
            str(output),
        ],
    )

    assert main() == 2
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["candidate"]["failed_gates"] == ["metric_minimum:ragas.faithfulness"]
    assert report["deltas"]["ragas.faithfulness"] == pytest.approx(-0.145)


def test_compare_cli_requires_external_metric_pair(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "compare",
            "--scenario",
            SCENARIO_PATH,
            "--baseline",
            RESPONSES_PATH,
            "--candidate",
            RESPONSES_PATH,
            "--baseline-external-metrics",
            "scenarios/japanese_troubleshooting/external-metrics-baseline.json",
        ],
    )

    with pytest.raises(SystemExit, match="both --baseline-external-metrics"):
        main()
