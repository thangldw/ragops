import json

import pytest

from ragops.cli import main
from ragops.config import load_sequential_policy
from ragops.loader import ContractError
from ragops.models import (
    MetricObservation,
    ReplayBundle,
    ReplayProvenance,
    SequentialPolicy,
    StatisticalMetricGate,
)
from ragops.sequential import compare_replay_bundles_sequentially


def _bundle(value, model, repeats):
    return ReplayBundle(
        schema_version="0.1",
        scenario_id="scenario",
        scenario_digest="sha256:scenario",
        provenance=ReplayProvenance(
            dataset="dataset",
            evidence=f"evidence-{model}",
            evaluator="evaluator",
            application="application",
            model=model,
            model_config=f"config-{model}",
            environment="environment",
        ),
        records=tuple(
            MetricObservation(
                f"case-{case}",
                f"run-{repeat:04d}",
                {"quality": value},
            )
            for case in range(3)
            for repeat in range(1, repeats + 1)
        ),
    )


def _policy():
    return SequentialPolicy(
        confidence=0.95,
        minimum_cases=3,
        minimum_repeats=2,
        maximum_repeats=4,
        look_every=1,
        resamples=200,
        seed=42,
        metric_gates={
            "quality": StatisticalMetricGate(
                direction="higher",
                minimum=0.9,
                max_regression=0.03,
            )
        },
    )


def test_sequential_gate_stops_early_for_pass() -> None:
    report = compare_replay_bundles_sequentially(
        _bundle(0.95, "baseline", 4),
        _bundle(0.95, "candidate", 4),
        _policy(),
    )

    assert report.decision == "pass"
    assert report.stopped_at_repeat == 2
    assert len(report.looks) == 1
    assert report.looks[0].boundary_confidence > 0.95


def test_sequential_gate_stops_early_for_clear_harm() -> None:
    report = compare_replay_bundles_sequentially(
        _bundle(0.95, "baseline", 4),
        _bundle(0.80, "candidate", 4),
        _policy(),
    )

    assert report.decision == "block"
    assert report.stopped_at_repeat == 2
    assert report.failed_gates == (
        "metric_absolute:quality",
        "metric_regression:quality",
    )


def test_sequential_gate_requests_more_evidence_before_first_look() -> None:
    report = compare_replay_bundles_sequentially(
        _bundle(0.95, "baseline", 1),
        _bundle(0.95, "candidate", 1),
        _policy(),
    )

    assert report.decision == "continue"
    assert report.failed_gates == ("sequential_incomplete",)
    assert report.looks == ()


def test_sequential_policy_and_environment_fail_closed() -> None:
    policy = load_sequential_policy("scenarios/statistical_gate/sequential-policy.toml")
    assert policy.maximum_repeats == 5
    candidate = _bundle(0.95, "candidate", 2)
    candidate = ReplayBundle(
        schema_version=candidate.schema_version,
        scenario_id=candidate.scenario_id,
        scenario_digest=candidate.scenario_digest,
        provenance=ReplayProvenance(
            **{**candidate.provenance.__dict__, "environment": "different"}
        ),
        records=candidate.records,
    )

    with pytest.raises(ContractError, match="infrastructure noise"):
        compare_replay_bundles_sequentially(
            _bundle(0.95, "baseline", 2), candidate, _policy()
        )


def test_compare_sequential_cli_passes_at_first_predeclared_look(monkeypatch, tmp_path) -> None:
    output = tmp_path / "sequential.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "compare-sequential",
            "--baseline-bundle",
            "scenarios/statistical_gate/baseline.json",
            "--candidate-bundle",
            "scenarios/statistical_gate/candidate-pass.json",
            "--policy",
            "scenarios/statistical_gate/sequential-policy.toml",
            "--format",
            "json",
            "--output",
            str(output),
        ],
    )

    assert main() == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["decision"] == "pass"
    assert report["stopped_at_repeat"] == 2
