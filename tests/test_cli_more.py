"""More in-process CLI coverage: workspaces, serve guards, pilot scaffold, usage logging."""

import json
import sys
from pathlib import Path

import pytest

from ragops import cli as cli_module
from ragops.cli import cli_entrypoint, main


@pytest.fixture()
def run(monkeypatch, capsys):
    def go(*args: str) -> tuple[int, str, str]:
        monkeypatch.setattr("sys.argv", ["ragops", *args])
        try:
            code = main()
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
            captured = capsys.readouterr()
            return code, captured.out, captured.err + ("" if isinstance(exc.code, int) else str(exc.code))
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return go


def test_workspace_lifecycle(run, tmp_path: Path) -> None:
    root = str(tmp_path / "cp")
    code, out, _ = run("workspace-create", "--root", root, "--workspace-id", "acme", "--name", "Acme")
    assert code == 0
    key = json.loads(out)["api_key"]
    code, _, err = run("workspace-create", "--root", root, "--workspace-id", "acme", "--name", "Acme")
    assert code != 0 and err
    code, out, _ = run("workspace-rotate-key", "--root", root, "--workspace-id", "acme", "--current-key", key)
    assert code == 0 and json.loads(out)["api_key"] != key
    code, _, err = run("workspace-rotate-key", "--root", root, "--workspace-id", "acme", "--current-key", key)
    assert code != 0
    code, out, _ = run("workspace-audit", "--root", root, "--workspace-id", "acme", "--limit", "5")
    assert code == 0 and isinstance(json.loads(out), list)


def test_serve_validates_port_and_dependency(run, monkeypatch) -> None:
    code, _, err = run("serve", "--port", "0")
    assert code != 0 and "port" in err
    monkeypatch.setitem(sys.modules, "uvicorn", None)
    code, _, err = run("serve")
    assert code != 0 and "api" in err.lower()


def test_pilot_init_creates_files_and_refuses_overwrite(run, tmp_path: Path) -> None:
    target = str(tmp_path / "pilot")
    code, out, _ = run("pilot-init", "--output", target, "--pilot-id", "pilot-1", "--label", "Pilot")
    assert code == 0 and json.loads(out)["created"]
    code, _, err = run("pilot-init", "--output", target, "--pilot-id", "pilot-1", "--label", "Pilot")
    assert code != 0 and "pilot contract error" in err


def test_usage_log_records_commands_and_report_summarizes(monkeypatch, capsys, tmp_path: Path) -> None:
    log = tmp_path / "usage.jsonl"
    monkeypatch.setenv("RAGOPS_USAGE_LOG", str(log))
    monkeypatch.setattr("sys.argv", ["ragops", "inspect", "--scenario", "scenarios/japanese_troubleshooting/scenario.json"])
    assert cli_entrypoint() == 0
    monkeypatch.setattr("sys.argv", ["ragops", "no-such-command"])
    with pytest.raises(SystemExit):
        cli_entrypoint()
    capsys.readouterr()
    monkeypatch.setattr("sys.argv", ["ragops", "usage-report", "--events", str(log)])
    assert cli_entrypoint() == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary
    monkeypatch.setattr("sys.argv", ["ragops", "usage-report", "--events", str(tmp_path / "missing.jsonl")])
    with pytest.raises(SystemExit):
        cli_entrypoint()


def test_usage_command_classification(monkeypatch) -> None:
    assert cli_module._usage_command([]) == "help"
    assert cli_module._usage_command(["--version"]) == "version"
    assert cli_module._usage_command(["evaluate"]) == "evaluate"
    assert cli_module._usage_command(["bogus"]) == "unknown"


def test_unwritable_usage_log_only_warns(monkeypatch, capsys, tmp_path: Path) -> None:
    monkeypatch.setenv("RAGOPS_USAGE_LOG", str(tmp_path))  # a directory, not a file
    monkeypatch.setattr("sys.argv", ["ragops", "inspect", "--scenario", "scenarios/japanese_troubleshooting/scenario.json"])
    assert cli_entrypoint() == 0
    assert "usage log warning" in capsys.readouterr().err


JA = "scenarios/japanese_troubleshooting"


def test_adapter_list_convert_and_errors(run, tmp_path: Path) -> None:
    code, out, _ = run("adapter", "list")
    assert code == 0 and "adapters" in json.loads(out)
    payload = tmp_path / "ragas.json"
    payload.write_text(json.dumps({"records": [{"case_id": "a", "faithfulness": 0.9}]}), encoding="utf-8")
    code, out, _ = run("adapter", "convert", "--profile", "ragas", "--input", str(payload),
                       "--case-id", "a", "--output", str(tmp_path / "env.json"))
    assert code == 0 and (tmp_path / "env.json").exists()
    phoenix = payload
    code, _, err = run("adapter", "convert", "--profile", "nope", "--input", str(phoenix / "annotations.json"),
                       "--output", str(tmp_path / "x.json"))
    assert code != 0 and "adapter error" in err
    code, _, err = run("adapter", "convert", "--profile", "ragas", "--input", str(tmp_path / "missing.json"),
                       "--output", str(tmp_path / "x.json"))
    assert code != 0 and "adapter error" in err


def test_trace_command_error_paths(run, tmp_path: Path) -> None:
    code, _, err = run("trace", "convert-otel", "--input", str(tmp_path / "missing.json"), "--output", str(tmp_path / "o.json"))
    assert code != 0 and "trace error" in err
    bad = tmp_path / "bad.json"
    bad.write_text("[1, 2]", encoding="utf-8")
    code, _, err = run("trace", "convert-otel", "--input", str(bad), "--output", str(tmp_path / "o.json"))
    assert code != 0 and "trace error" in err
    code, _, err = run("trace", "evaluate", "--trace", str(bad), "--expectation", str(bad))
    assert code != 0 and "trace error" in err


def test_history_and_review_with_a_store(run, tmp_path: Path) -> None:
    store = str(tmp_path / "runs.db")
    code, _, _ = run("evaluate", "--scenario", f"{JA}/scenario.json", "--responses", f"{JA}/sample_responses.json",
                     "--store", store, "--label", "first", "--format", "json")
    assert code == 0
    code, out, _ = run("history", "--store", store, "--limit", "5")
    runs = json.loads(out)
    assert code == 0 and len(runs) == 1
    run_id = str(runs[0]["id"] if "id" in runs[0] else runs[0]["run_id"])
    code, out, _ = run("review", "--store", store, "--run-id", run_id, "--status", "accepted", "--reviewer", "lead")
    assert code == 0 and json.loads(out)["review_status"] == "accepted"
    code, _, err = run("review", "--store", store, "--run-id", "does-not-exist", "--status", "accepted", "--reviewer", "lead")
    assert code != 0


def test_baseline_sign_and_provenance_errors(run, tmp_path: Path) -> None:
    missing = str(tmp_path / "missing.json")
    code, _, err = run("baseline-sign", "--manifest", missing, "--key", missing, "--output", str(tmp_path / "s"))
    assert code != 0 and "baseline" in err
    code, _, err = run("diagnose-provenance", "--reference-bundle", missing, "--current-bundle", missing)
    assert code != 0
