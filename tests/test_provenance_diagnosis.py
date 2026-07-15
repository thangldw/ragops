from dataclasses import replace

from ragops.provenance import diagnose_provenance
from ragops.statistical import load_replay_bundle


FIXTURES = "scenarios/statistical_gate"


def test_model_regression_is_isolated_from_recorded_provenance() -> None:
    diagnosis = diagnose_provenance(
        load_replay_bundle(f"{FIXTURES}/baseline.json"),
        load_replay_bundle(f"{FIXTURES}/candidate-pass.json"),
    )

    assert diagnosis.classification == "model_regression"
    assert diagnosis.comparable
    assert diagnosis.causal_axes == ("model",)
    assert diagnosis.evidence_changed


def test_evaluator_dataset_and_infrastructure_axes_are_distinct() -> None:
    reference = load_replay_bundle(f"{FIXTURES}/baseline.json")
    evaluator = replace(
        reference,
        provenance=replace(reference.provenance, evaluator="judge-v2"),
    )
    dataset = replace(
        reference,
        provenance=replace(reference.provenance, dataset="dataset-v2"),
    )
    infrastructure = replace(
        reference,
        provenance=replace(reference.provenance, environment="runner-v2"),
    )

    assert diagnose_provenance(reference, evaluator).classification == "evaluator_drift"
    assert diagnose_provenance(reference, dataset).classification == "dataset_drift"
    assert (
        diagnose_provenance(reference, infrastructure).classification
        == "infrastructure_noise"
    )


def test_multiple_causal_axes_are_confounded() -> None:
    reference = load_replay_bundle(f"{FIXTURES}/baseline.json")
    current = replace(
        reference,
        provenance=replace(
            reference.provenance,
            model="model-v2",
            evaluator="judge-v2",
        ),
    )

    diagnosis = diagnose_provenance(reference, current)

    assert diagnosis.classification == "confounded"
    assert not diagnosis.comparable
