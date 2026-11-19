"""In-process CLI tests: exercise argument handling and error paths of many commands."""

import json
from pathlib import Path

import pytest

from ragops.cli import main

JA = Path("scenarios/japanese_troubleshooting")
SCENARIO = str(JA / "scenario.json")
RESPONSES = str(JA / "sample_responses.json")
REGRESSED = str(JA / "regressed_responses.json")


@pytest.fixture()
def cli(monkeypatch, capsys):
    def run(*args: str) -> tuple[int, str, str]:
        monkeypatch.setattr("sys.argv", ["ragops", *args])
        try:
            code = main()
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
            captured = capsys.readouterr()
            return code, captured.out, captured.err + (str(exc.code) if not isinstance(exc.code, int) else "")
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    return run


def test_inspect_and_missing_scenario(cli) -> None:
    code, out, _ = cli("inspect", "--scenario", SCENARIO)
    assert code == 0 and json.loads(out)
    code, _, err = cli("inspect", "--scenario", "nope.json")
    assert code != 0 and "contract error" in err


def test_evaluate_formats_output_and_store(cli, tmp_path: Path) -> None:
    store = tmp_path / "runs.db"
    out_file = tmp_path / "report.md"
    code, _, _ = cli(
        "evaluate", "--scenario", SCENARIO, "--responses", RESPONSES,
        "--format", "markdown", "--output", str(out_file), "--store", str(store), "--label", "ci",
    )
    assert code == 0 and "RAGOps evaluation" in out_file.read_text(encoding="utf-8")
    code, out, _ = cli("history", "--store", str(store))
    runs = json.loads(out)
    assert code == 0 and runs[0]["label"] == "ci"
    run_id = runs[0]["id"]
    code, out, _ = cli(
        "review", "--store", str(store), "--run-id", run_id, "--status", "accepted", "--reviewer", "qa"
    )
    assert code == 0
    code, out, _ = cli("trend", "--store", str(store), "--scenario-id", runs[0]["scenario_id"],
                       "--metric", "citation_coverage")
    assert code == 0 and json.loads(out)


def test_compare_markdown_html_and_regression_exit(cli, tmp_path: Path) -> None:
    benchmark = str(JA / "benchmark-v0.2.json")
    base, bad = str(JA / "benchmark-baseline.json"), str(JA / "benchmark-regressed.json")
    code, _, _ = cli("compare", "--scenario", benchmark, "--baseline", base, "--candidate", bad)
    assert code == 2
    html = tmp_path / "r.html"
    code, _, _ = cli(
        "compare", "--scenario", benchmark, "--baseline", base, "--candidate", bad,
        "--format", "html", "--output", str(html),
    )
    assert code == 2 and html.read_text(encoding="utf-8").lstrip().lower().startswith("<!doctype html>")
    code, out, _ = cli("compare", "--scenario", benchmark, "--baseline", base, "--candidate", base,
                       "--format", "json")
    assert code == 0 and json.loads(out)["passed"] is True


def test_contract_commands(cli, tmp_path: Path) -> None:
    code, out, _ = cli("contract", "diff", "--kind", "scenario", "--from", "0.1", "--to", "0.2")
    assert code == 0 and json.loads(out)
    code, out, _ = cli("contract", "validate", "--input", SCENARIO)
    assert code == 0
    migrated = tmp_path / "migrated.json"
    legacy = json.loads(Path(SCENARIO).read_text(encoding="utf-8"))
    legacy["schema_version"] = "0.1"
    source = tmp_path / "old.json"
    source.write_text(json.dumps(legacy), encoding="utf-8")
    code, _, _ = cli(
        "contract", "migrate", "--kind", "scenario", "--from", "0.1", "--to", "0.2",
        "--input", str(source), "--output", str(migrated),
    )
    assert code in (0, 1) and (code != 0 or migrated.exists())
    code, _, err = cli("contract", "validate", "--input", str(tmp_path / "missing.json"))
    assert code != 0


def test_trace_otel_convert_and_error(cli, tmp_path: Path) -> None:
    code, _, err = cli("trace", "convert-otel", "--input", str(tmp_path / "none.json"),
                       "--output", str(tmp_path / "o.json"))
    assert code != 0 and "trace error" in err
    code, _, err = cli("trace", "evaluate", "--trace", str(tmp_path / "a.json"),
                       "--expectation", str(tmp_path / "b.json"))
    assert code != 0 and "trace error" in err


def test_governance_lifecycle(cli, tmp_path: Path) -> None:
    store = str(tmp_path / "gov.db")
    common = ["--store", store, "--artifact-id", "baseline-1"]
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps({"scenario_id": "support"}), encoding="utf-8")
    code, out, _ = cli(
        "governance", "register", *common, "--kind", "baseline",
        "--digest", "a" * 64, "--metadata", str(metadata), "--actor", "alice",
    )
    assert code == 0, out
    code, out, _ = cli("governance", "transition", *common, "--state", "reviewed", "--actor", "alice")
    assert code == 0
    code, out, _ = cli("governance", "review", *common, "--reviewer", "bob", "--verdict", "approve")
    assert code == 0 and json.loads(out) == {"recorded": True}
    code, out, _ = cli("governance", "queue", "--store", store, "--reviewer", "bob")
    assert code == 0 and "artifacts" in json.loads(out)
    code, out, _ = cli("governance", "audit", *common)
    assert code == 0 and json.loads(out)["events"]
    code, _, err = cli("governance", "transition", "--store", store, "--artifact-id", "ghost",
                       "--state", "accepted", "--actor", "x")
    assert code != 0 and "governance error" in err


def test_demo_serve_and_usage_report_errors(cli, tmp_path: Path) -> None:
    code, out, _ = cli("demo", "--output", str(tmp_path / "demo"))
    assert code == 0 and json.loads(out)
    code, _, err = cli("demo", "--output", str(tmp_path / "demo"))
    assert code != 0 and "demo output error" in err
    code, _, err = cli("serve", "--port", "0")
    assert code != 0 and "port" in err
    code, _, err = cli("usage-report", "--events", str(tmp_path / "none.jsonl"))
    assert code != 0 and "usage contract error" in err


def test_baseline_verify_requires_complete_signature_options(cli, tmp_path: Path) -> None:
    code, _, err = cli("baseline-verify", "--manifest", "m.json", "--bundle", "b.json",
                       "--policy", "p.toml", "--signature", "s.sig")
    assert code != 0 and "signature verification requires" in err


GATE = Path("scenarios/statistical_gate")


def test_statistical_and_sequential_gates_in_process(cli, tmp_path: Path) -> None:
    base, passing, blocking = (str(GATE / name) for name in ("baseline.json", "candidate-pass.json", "candidate-block.json"))
    policy = str(GATE / "policy.toml")
    code, out, _ = cli("compare-runs", "--baseline-bundle", base, "--candidate-bundle", passing, "--policy", policy)
    assert code == 0
    out_file = tmp_path / "block.md"
    code, _, _ = cli(
        "compare-runs", "--baseline-bundle", base, "--candidate-bundle", blocking, "--policy", policy,
        "--output", str(out_file),
    )
    assert code == 2 and out_file.read_text(encoding="utf-8")
    code, _, err = cli("compare-runs", "--baseline-bundle", "nope", "--candidate-bundle", base, "--policy", policy)
    assert code != 0

    code, out, _ = cli(
        "compare-sequential", "--baseline-bundle", base, "--candidate-bundle", passing,
        "--policy", str(GATE / "sequential-policy.toml"),
    )
    assert code in (0, 2, 3)
    code, _, _ = cli(
        "compare-sequential", "--baseline-bundle", "nope", "--candidate-bundle", base,
        "--policy", str(GATE / "sequential-policy.toml"),
    )
    assert code != 0


def test_evaluator_drift_and_provenance_in_process(cli) -> None:
    base = str(GATE / "baseline.json")
    code, _, err = cli(
        "detect-evaluator-drift", "--reference-bundle", base, "--current-bundle", base,
        "--policy", str(GATE / "drift-policy.toml"), "--format", "json",
    )
    assert code != 0 and "different evaluator provenance" in err
    code, _, _ = cli("detect-evaluator-drift", "--reference-bundle", "nope", "--current-bundle", base,
                     "--policy", str(GATE / "drift-policy.toml"))
    assert code != 0
    code, out, _ = cli("diagnose-provenance", "--reference-bundle", base, "--current-bundle",
                       str(GATE / "candidate-pass.json"))
    assert code == 0 and json.loads(out)


def test_baseline_create_and_verify_in_process(cli, tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    code, _, _ = cli(
        "baseline-create", "--bundle", str(GATE / "baseline.json"), "--policy", str(GATE / "policy.toml"),
        "--owner", "qa", "--accepted-at", "2026-07-15T21:00:00+09:00", "--output", str(manifest),
    )
    assert code == 0 and manifest.exists()
    code, out, _ = cli("baseline-verify", "--manifest", str(manifest), "--bundle", str(GATE / "baseline.json"),
                       "--policy", str(GATE / "policy.toml"))
    assert code == 0 and json.loads(out)["verified"] is True
    code, _, err = cli("baseline-verify", "--manifest", str(manifest), "--bundle", str(GATE / "candidate-pass.json"),
                       "--policy", str(GATE / "policy.toml"))
    assert code != 0 and "baseline verification error" in err
    code, _, err = cli("baseline-create", "--bundle", "nope", "--policy", str(GATE / "policy.toml"),
                       "--owner", "qa", "--accepted-at", "2026-07-15T21:00:00Z", "--output", str(manifest))
    assert code != 0


def test_dataset_and_evidence_commands_in_process(cli, tmp_path: Path) -> None:
    manifest = tmp_path / "dataset.json"
    scenario = json.loads(Path(SCENARIO).read_text(encoding="utf-8"))
    ids = ",".join(case["id"] for case in scenario["cases"])
    code, _, err = cli(
        "dataset", "create", "--scenario", SCENARIO, "--dataset-id", "ds", "--version", "1.0.0",
        "--source-classification", "synthetic", "--owner", "qa", "--split", f"test={ids}",
        "--reviewed", "--output", str(manifest),
    )
    assert code == 0 and manifest.exists(), err
    code, out, _ = cli("dataset", "validate", "--manifest", str(manifest))
    assert code in (0, 2) and json.loads(out)
    code, out, _ = cli("dataset", "diff", "--before", str(manifest), "--after", str(manifest))
    assert code == 0
    code, _, err = cli("dataset", "validate", "--manifest", str(tmp_path / "missing.json"))
    assert code != 0
    artifact = tmp_path / "a.txt"
    artifact.write_text("evidence", encoding="utf-8")
    bundle = tmp_path / "bundle"
    code, _, _ = cli("evidence", "create", "--bundle", str(bundle), "--decision", "PASS",
                     "--artifact", f"note={artifact}", "--limitation", "synthetic",
                     "--created-at", "2026-01-01T00:00:00Z")
    assert code == 0
    code, out, _ = cli("evidence", "verify", "--bundle", str(bundle))
    assert code == 0
    tampered = next(path for path in bundle.rglob("*") if path.is_file() and path.name != "manifest.json")
    tampered.write_text("tampered", encoding="utf-8")
    code, _, err = cli("evidence", "verify", "--bundle", str(bundle))
    assert code != 0
    code, _, err = cli("evidence", "verify", "--bundle", str(tmp_path / "missing"))
    assert code != 0
