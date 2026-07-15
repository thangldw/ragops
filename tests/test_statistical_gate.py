import json

import pytest

from ragops.cli import main
from ragops.config import load_statistical_policy
from ragops.loader import ContractError
from ragops.models import StatisticalMetricGate, StatisticalPolicy
from ragops.statistical import compare_replay_bundles, replay_bundle_from_dict


FIXTURES = "scenarios/statistical_gate"


def _bundle(
    values,
    *,
    application="application",
    model="model",
    model_config="model-config",
    environment="environment",
    dataset="dataset",
    evidence="evidence",
    evaluator="evaluator",
    scenario_digest="sha256:scenario",
):
    records = []
    for case_index, case_values in enumerate(values, start=1):
        for repeat_index, value in enumerate(case_values, start=1):
            records.append(
                {
                    "case_id": f"case-{case_index}",
                    "repeat_id": f"run-{repeat_index}",
                    "metrics": {"quality": value},
                }
            )
    return replay_bundle_from_dict(
        {
            "schema_version": "0.1",
            "scenario_id": "scenario",
            "scenario_digest": scenario_digest,
            "provenance": {
                "dataset": dataset,
                "evidence": evidence,
                "evaluator": evaluator,
                "application": application,
                "model": model,
                "model_config": model_config,
                "environment": environment,
            },
            "records": records,
        }
    )


def _policy(*, minimum_cases=3, direction="higher"):
    return StatisticalPolicy(
        confidence=0.95,
        minimum_cases=minimum_cases,
        resamples=200,
        seed=42,
        metric_gates={
            "quality": StatisticalMetricGate(
                direction=direction,
                minimum=0.9 if direction == "higher" else None,
                maximum=150.0 if direction == "lower" else None,
                max_regression=0.03 if direction == "higher" else 15.0,
            )
        },
    )


def test_statistical_gate_passes_and_is_deterministic() -> None:
    baseline = _bundle([[0.95, 0.95], [0.95, 0.95], [0.95, 0.95]], model="base")
    candidate = _bundle([[0.94, 0.94], [0.94, 0.94], [0.94, 0.94]], model="candidate")

    first = compare_replay_bundles(baseline, candidate, _policy())
    second = compare_replay_bundles(baseline, candidate, _policy())

    assert first == second
    assert first.passed
    assert first.metrics["quality"].candidate_bound == pytest.approx(0.94)
    assert first.metrics["quality"].regression_bound == pytest.approx(-0.01)
    assert first.provenance["baseline"]["model"] == "base"
    assert first.provenance["changed_axes"] == ["model"]


def test_statistical_gate_blocks_absolute_and_regression_failure() -> None:
    baseline = _bundle([[0.95], [0.95], [0.95]], model="base")
    candidate = _bundle([[0.85], [0.85], [0.85]], model="candidate")

    report = compare_replay_bundles(baseline, candidate, _policy())

    assert not report.passed
    assert report.failed_gates == (
        "metric_absolute:quality",
        "metric_regression:quality",
    )


def test_statistical_gate_blocks_insufficient_distinct_cases() -> None:
    baseline = _bundle([[0.95, 0.95], [0.95, 0.95]])
    candidate = _bundle([[0.95, 0.95], [0.95, 0.95]])

    report = compare_replay_bundles(baseline, candidate, _policy(minimum_cases=3))

    assert not report.passed
    assert report.failed_gates == ("insufficient_cases",)
    assert report.metrics["quality"].candidate_bound is None


def test_lower_is_better_gate_uses_upper_bounds() -> None:
    baseline = _bundle([[100.0], [100.0], [100.0]])
    candidate = _bundle([[110.0], [110.0], [110.0]])

    report = compare_replay_bundles(
        baseline,
        candidate,
        _policy(direction="lower"),
    )

    assert report.passed
    assert report.metrics["quality"].candidate_bound == pytest.approx(110.0)
    assert report.metrics["quality"].regression_bound == pytest.approx(10.0)


def test_replay_contract_rejects_duplicates_and_provenance_mismatch() -> None:
    baseline = _bundle([[0.95], [0.95], [0.95]], dataset="old")
    candidate = _bundle([[0.95], [0.95], [0.95]], dataset="new")

    with pytest.raises(ContractError, match="dataset provenance"):
        compare_replay_bundles(baseline, candidate, _policy())

    changed_scenario = _bundle(
        [[0.95], [0.95], [0.95]],
        dataset="old",
        scenario_digest="sha256:changed",
    )
    with pytest.raises(ContractError, match="scenario digests"):
        compare_replay_bundles(baseline, changed_scenario, _policy())

    raw = {
        "schema_version": "0.1",
        "scenario_id": "scenario",
        "scenario_digest": "sha256:scenario",
        "provenance": {
            "dataset": "d",
            "evidence": "r",
            "evaluator": "e",
            "application": "a",
            "model": "m",
            "model_config": "c",
            "environment": "env",
        },
        "records": [
            {"case_id": "one", "repeat_id": "one", "metrics": {"quality": 1.0}},
            {"case_id": "one", "repeat_id": "one", "metrics": {"quality": 1.0}},
        ],
    }
    with pytest.raises(ContractError, match="identities must be unique"):
        replay_bundle_from_dict(raw)


def test_replay_contract_rejects_inconsistent_metrics_and_case_coverage() -> None:
    raw = {
        "schema_version": "0.1",
        "scenario_id": "scenario",
        "scenario_digest": "sha256:scenario",
        "provenance": {
            "dataset": "d",
            "evidence": "r",
            "evaluator": "e",
            "application": "a",
            "model": "m",
            "model_config": "c",
            "environment": "env",
        },
        "records": [
            {"case_id": "one", "repeat_id": "one", "metrics": {"quality": 1.0}},
            {"case_id": "two", "repeat_id": "one", "metrics": {"latency": 1.0}},
        ],
    }
    with pytest.raises(ContractError, match="same metric names"):
        replay_bundle_from_dict(raw)

    baseline = _bundle([[0.95], [0.95], [0.95]])
    candidate = _bundle([[0.95], [0.95]])
    with pytest.raises(ContractError, match="case coverage mismatch"):
        compare_replay_bundles(baseline, candidate, _policy())


def test_direct_statistical_policy_is_validated_by_core() -> None:
    baseline = _bundle([[0.95], [0.95], [0.95]])
    candidate = _bundle([[0.95], [0.95], [0.95]])
    invalid = StatisticalPolicy(
        confidence=1.0,
        minimum_cases=3,
        resamples=200,
        seed=1,
        metric_gates=_policy().metric_gates,
    )

    with pytest.raises(ContractError, match="confidence"):
        compare_replay_bundles(baseline, candidate, invalid)


def test_loads_statistical_policy() -> None:
    policy = load_statistical_policy(f"{FIXTURES}/policy.toml")

    assert policy.confidence == 0.95
    assert policy.metric_gates["citation_precision"].minimum == 0.9
    assert policy.metric_gates["citation_precision"].max_regression == 0.03


@pytest.mark.parametrize(
    "content, message",
    [
        ("[statistical]\nconfidence = 1.0\n", "confidence"),
        (
            "[statistical]\nconfidence=0.95\nminimum_cases=1\nresamples=99\nseed=1\n"
            "[statistical.metrics.quality]\ndirection='higher'\nminimum=0.9\n"
            "max_regression=0.1\n",
            "at least 100",
        ),
        (
            "[statistical]\nconfidence=0.95\nminimum_cases=1\nresamples=100\nseed=1\n"
            "[statistical.metrics.quality]\ndirection='higher'\nmaximum=1\n"
            "max_regression=0.1\n",
            "requires minimum",
        ),
    ],
)
def test_rejects_invalid_statistical_policy(tmp_path, content, message) -> None:
    path = tmp_path / "policy.toml"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_statistical_policy(path)


def test_compare_runs_cli_writes_json_and_preserves_gate_exit(monkeypatch, tmp_path) -> None:
    output = tmp_path / "report.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "compare-runs",
            "--baseline-bundle",
            f"{FIXTURES}/baseline.json",
            "--candidate-bundle",
            f"{FIXTURES}/candidate-pass.json",
            "--policy",
            f"{FIXTURES}/policy.toml",
            "--format",
            "json",
            "--output",
            str(output),
        ],
    )

    assert main() == 0
    assert json.loads(output.read_text(encoding="utf-8"))["passed"] is True

    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "compare-runs",
            "--baseline-bundle",
            f"{FIXTURES}/baseline.json",
            "--candidate-bundle",
            f"{FIXTURES}/candidate-block.json",
            "--policy",
            f"{FIXTURES}/policy.toml",
        ],
    )
    assert main() == 2
