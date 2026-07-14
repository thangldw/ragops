import json
from pathlib import Path

import pytest

from ragops.cli import main
from ragops.pilot import (
    PilotContractError,
    load_pilot_economics,
    load_pilot_manifest,
    load_pilot_observations,
    pilot_markdown,
    summarize_pilot,
)

FIXTURES = Path("docs/gtm/pilot-fixtures")


def load_report():
    return summarize_pilot(
        load_pilot_manifest(FIXTURES / "synthetic-manifest.json"),
        load_pilot_observations(FIXTURES / "synthetic-observations.jsonl"),
        load_pilot_economics(FIXTURES / "synthetic-economics.json"),
    )


def test_synthetic_pilot_report_separates_metrics_and_estimates() -> None:
    report = load_report()

    assert report.synthetic is True
    assert report.decision == "SCALE"
    assert report.failed_conditions == ()
    assert report.metrics["activation_rate"] == 1.0
    assert report.metrics["repeat_usage_rate"] == 1.0
    assert report.metrics["task_success_uplift"] == pytest.approx(1 / 3)
    assert report.metrics["pilot_critical_incidents"] == 0
    assert report.economic_estimates["estimated_roi"] > 0
    markdown = pilot_markdown(report)
    assert "SYNTHETIC EXAMPLE — NOT CUSTOMER EVIDENCE" in markdown
    assert "does not establish causality" in markdown
    assert markdown == pilot_markdown(load_report())


def test_pilot_cli_writes_markdown(monkeypatch, tmp_path: Path) -> None:
    output = tmp_path / "pilot.md"
    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "pilot-report",
            "--manifest",
            str(FIXTURES / "synthetic-manifest.json"),
            "--observations",
            str(FIXTURES / "synthetic-observations.jsonl"),
            "--economics",
            str(FIXTURES / "synthetic-economics.json"),
            "--output",
            str(output),
        ],
    )

    assert main() == 0
    assert "Decision: SCALE" in output.read_text(encoding="utf-8")


def test_pilot_rejects_duplicate_tasks(tmp_path: Path) -> None:
    source = FIXTURES / "synthetic-observations.jsonl"
    first = source.read_text(encoding="utf-8").splitlines()[0]
    path = tmp_path / "duplicate.jsonl"
    path.write_text(first + "\n" + first + "\n", encoding="utf-8")

    with pytest.raises(PilotContractError, match="task_id values must be unique"):
        load_pilot_observations(path)


def test_pilot_rejects_unknown_user_or_missing_cohort(tmp_path: Path) -> None:
    observations = load_pilot_observations(FIXTURES / "synthetic-observations.jsonl")
    manifest_data = json.loads((FIXTURES / "synthetic-manifest.json").read_text())
    manifest_data["eligible_user_ids"] = ["user_001"]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest_data), encoding="utf-8")

    with pytest.raises(PilotContractError, match="eligible cohort"):
        summarize_pilot(load_pilot_manifest(path), observations)


def test_critical_incident_forces_hold() -> None:
    manifest = load_pilot_manifest(FIXTURES / "synthetic-manifest.json")
    observations = list(load_pilot_observations(FIXTURES / "synthetic-observations.jsonl"))
    incident = observations[-1]
    observations[-1] = type(incident)(**{**incident.__dict__, "critical_incident": True})

    report = summarize_pilot(manifest, tuple(observations))
    assert report.decision == "HOLD"
    assert "critical_incidents" in report.failed_conditions


def test_pilot_contract_rejects_unknown_fields(tmp_path: Path) -> None:
    manifest_data = json.loads((FIXTURES / "synthetic-manifest.json").read_text())
    manifest_data["raw_customer_email"] = "must not be collected"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest_data), encoding="utf-8")

    with pytest.raises(PilotContractError, match="unexpected fields"):
        load_pilot_manifest(path)
