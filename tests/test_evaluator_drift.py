import json

import pytest

from ragops.adapters.repeated_runs import write_replay_bundle
from ragops.cli import main
from ragops.config import load_evaluator_drift_policy
from ragops.drift import detect_evaluator_drift
from ragops.loader import ContractError
from ragops.models import (
    EvaluatorDriftMetricGate,
    EvaluatorDriftPolicy,
    MetricObservation,
    ReplayBundle,
    ReplayProvenance,
)


def _bundle(value, evaluator, *, cases=3, evidence="frozen-responses"):
    return ReplayBundle(
        schema_version="0.1",
        scenario_id="anchor-scenario",
        scenario_digest="sha256:anchor-scenario",
        provenance=ReplayProvenance(
            dataset="anchor-dataset",
            evidence=evidence,
            evaluator=evaluator,
            application="frozen-application",
            model="frozen-model",
            model_config="frozen-config",
            environment="offline-anchor-runner",
        ),
        records=tuple(
            MetricObservation(f"case-{case}", "run-0001", {"citation_precision": value})
            for case in range(cases)
        ),
    )


def _policy(minimum_cases=3):
    return EvaluatorDriftPolicy(
        confidence=0.95,
        minimum_cases=minimum_cases,
        resamples=200,
        seed=42,
        metric_gates={"citation_precision": EvaluatorDriftMetricGate(0.02)},
    )


def test_evaluator_equivalence_passes_with_frozen_anchors() -> None:
    report = detect_evaluator_drift(
        _bundle(0.95, "judge-v1"),
        _bundle(0.96, "judge-v2"),
        _policy(),
    )

    assert report.passed
    assert report.metrics["citation_precision"].lower_bound == pytest.approx(0.01)
    assert report.metrics["citation_precision"].upper_bound == pytest.approx(0.01)


def test_evaluator_drift_blocks_and_insufficient_evidence_is_named() -> None:
    drifted = detect_evaluator_drift(
        _bundle(0.95, "judge-v1"),
        _bundle(0.90, "judge-v2"),
        _policy(),
    )
    insufficient = detect_evaluator_drift(
        _bundle(0.95, "judge-v1", cases=2),
        _bundle(0.95, "judge-v2", cases=2),
        _policy(),
    )

    assert drifted.failed_gates == ("evaluator_drift:citation_precision",)
    assert insufficient.failed_gates == ("insufficient_cases",)
    assert insufficient.metrics["citation_precision"].lower_bound is None


def test_evaluator_drift_rejects_confounded_anchors() -> None:
    with pytest.raises(ContractError, match=r"changed=\['evidence'\]"):
        detect_evaluator_drift(
            _bundle(0.95, "judge-v1", evidence="old-responses"),
            _bundle(0.95, "judge-v2", evidence="new-responses"),
            _policy(),
        )


def test_loads_drift_policy() -> None:
    policy = load_evaluator_drift_policy("scenarios/statistical_gate/drift-policy.toml")

    assert policy.metric_gates["citation_precision"].max_absolute_change == 0.02


def test_evaluator_drift_cli_writes_report(monkeypatch, tmp_path) -> None:
    reference = tmp_path / "reference.json"
    current = tmp_path / "current.json"
    output = tmp_path / "drift.json"
    write_replay_bundle(reference, _bundle(0.95, "judge-v1"))
    write_replay_bundle(current, _bundle(0.96, "judge-v2"))
    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "detect-evaluator-drift",
            "--reference-bundle",
            str(reference),
            "--current-bundle",
            str(current),
            "--policy",
            "scenarios/statistical_gate/drift-policy.toml",
            "--format",
            "json",
            "--output",
            str(output),
        ],
    )

    assert main() == 0
    assert json.loads(output.read_text(encoding="utf-8"))["passed"] is True
