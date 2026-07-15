import json
from dataclasses import replace
from pathlib import Path

from jsonschema.validators import validator_for

from ragops.baseline import create_baseline_manifest
from ragops.config import (
    load_evaluator_drift_policy,
    load_sequential_policy,
    load_statistical_policy,
)
from ragops.drift import detect_evaluator_drift
from ragops.provenance import diagnose_provenance
from ragops.sequential import compare_replay_bundles_sequentially
from ragops.statistical import compare_replay_bundles, load_replay_bundle


FIXTURES = Path("scenarios/statistical_gate")
SCHEMAS = Path("schemas")


def _validate(schema_name, instance) -> None:
    schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
    validator = validator_for(schema)
    validator.check_schema(schema)
    validator(schema).validate(json.loads(json.dumps(instance)))


def test_replay_plan_and_fixed_report_match_published_schemas() -> None:
    baseline_data = json.loads((FIXTURES / "baseline.json").read_text(encoding="utf-8"))
    plan_data = json.loads((FIXTURES / "run-plan.json").read_text(encoding="utf-8"))
    baseline = load_replay_bundle(FIXTURES / "baseline.json")
    candidate = load_replay_bundle(FIXTURES / "candidate-pass.json")
    report = compare_replay_bundles(
        baseline, candidate, load_statistical_policy(FIXTURES / "policy.toml")
    )

    _validate("replay-bundle-0.1.schema.json", baseline_data)
    _validate("repeated-run-plan-0.1.schema.json", plan_data)
    _validate("statistical-report-0.1.schema.json", report.to_dict())


def test_sequential_drift_provenance_and_manifest_instances_match_schemas() -> None:
    baseline = load_replay_bundle(FIXTURES / "baseline.json")
    candidate = load_replay_bundle(FIXTURES / "candidate-pass.json")
    sequential = compare_replay_bundles_sequentially(
        baseline,
        candidate,
        load_sequential_policy(FIXTURES / "sequential-policy.toml"),
    )
    current_evaluator = replace(
        baseline,
        provenance=replace(baseline.provenance, evaluator="citation-precision-v2"),
    )
    drift = detect_evaluator_drift(
        baseline,
        current_evaluator,
        load_evaluator_drift_policy(FIXTURES / "drift-policy.toml"),
    )
    diagnosis = diagnose_provenance(baseline, candidate)
    manifest = create_baseline_manifest(
        FIXTURES / "baseline.json",
        FIXTURES / "policy.toml",
        owner="thang",
        accepted_at="2026-07-15T21:00:00+09:00",
    )

    _validate("sequential-report-0.1.schema.json", sequential.to_dict())
    _validate("evaluator-drift-report-0.1.schema.json", drift.to_dict())
    _validate("provenance-diagnosis-0.1.schema.json", diagnosis.to_dict())
    _validate("baseline-manifest-0.1.schema.json", manifest.to_dict())
