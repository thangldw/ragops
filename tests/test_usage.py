import json
import os
import subprocess
import sys
from pathlib import Path


def run_cli(*args: str, usage_log: Path | None = None) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    if usage_log is None:
        environment.pop("RAGOPS_USAGE_LOG", None)
    else:
        environment["RAGOPS_USAGE_LOG"] = str(usage_log)
    return subprocess.run(
        [sys.executable, "-m", "ragops.cli", *args],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )


def test_opt_in_usage_event_omits_arguments_and_paths(tmp_path: Path) -> None:
    usage_log = tmp_path / "usage.jsonl"
    sensitive_output = tmp_path / "customer-secret-project"

    result = run_cli(
        "demo",
        "--output",
        str(sensitive_output),
        usage_log=usage_log,
    )

    assert result.returncode == 0
    event = json.loads(usage_log.read_text(encoding="utf-8"))
    assert event["schema_version"] == "ragops-local-usage-event-0.1"
    assert event["command"] == "demo"
    assert event["exit_code"] == 0
    assert set(event) == {
        "schema_version",
        "recorded_at",
        "ragops_version",
        "command",
        "exit_code",
    }
    assert "customer-secret-project" not in usage_log.read_text(encoding="utf-8")


def test_usage_report_aggregates_literal_events(tmp_path: Path) -> None:
    events = tmp_path / "usage.jsonl"
    events.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "schema_version": "ragops-local-usage-event-0.1",
                        "recorded_at": "2026-08-21T10:00:00Z",
                        "ragops_version": "2.0.1",
                        "command": "demo",
                        "exit_code": 0,
                    }
                ),
                json.dumps(
                    {
                        "schema_version": "ragops-local-usage-event-0.1",
                        "recorded_at": "2026-08-22T10:00:00Z",
                        "ragops_version": "2.0.1",
                        "command": "demo",
                        "exit_code": 2,
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_cli("usage-report", "--events", str(events), "--format", "json")

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report == {
        "report_version": "ragops-local-usage-report-0.1",
        "event_count": 2,
        "first_recorded_at": "2026-08-21T10:00:00Z",
        "last_recorded_at": "2026-08-22T10:00:00Z",
        "command_counts": {"demo": 2},
        "exit_code_counts": {"0": 1, "2": 1},
    }


def test_usage_report_rejects_unknown_contract_version(tmp_path: Path) -> None:
    events = tmp_path / "usage.jsonl"
    events.write_text('{"schema_version":"unknown"}\n', encoding="utf-8")

    result = run_cli("usage-report", "--events", str(events), "--format", "json")

    assert result.returncode == 1
    assert "usage contract error" in result.stderr


def test_usage_log_failure_does_not_change_command_exit_code(tmp_path: Path) -> None:
    result = run_cli("--version", usage_log=tmp_path)

    assert result.returncode == 0
    assert result.stdout.strip() == "ragops 2.0.2"
    assert "usage log warning" in result.stderr


def test_invalid_command_text_is_recorded_as_unknown(tmp_path: Path) -> None:
    usage_log = tmp_path / "usage.jsonl"

    result = run_cli("customer-secret-project", usage_log=usage_log)

    assert result.returncode == 2
    event = json.loads(usage_log.read_text(encoding="utf-8"))
    assert event["command"] == "unknown"
    assert "customer-secret-project" not in usage_log.read_text(encoding="utf-8")


def test_usage_report_orders_fractional_timestamps_chronologically(tmp_path: Path) -> None:
    events = tmp_path / "usage.jsonl"
    common = {
        "schema_version": "ragops-local-usage-event-0.1",
        "ragops_version": "2.0.1",
        "command": "demo",
        "exit_code": 0,
    }
    events.write_text(
        json.dumps({**common, "recorded_at": "2026-08-21T10:00:00.100000Z"})
        + "\n"
        + json.dumps({**common, "recorded_at": "2026-08-21T10:00:00Z"})
        + "\n",
        encoding="utf-8",
    )

    result = run_cli("usage-report", "--events", str(events), "--format", "json")

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["first_recorded_at"] == "2026-08-21T10:00:00Z"
    assert report["last_recorded_at"] == "2026-08-21T10:00:00.100000Z"
