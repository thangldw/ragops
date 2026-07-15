import json
import sys
from pathlib import Path

import pytest

from ragops.adapters.repeated_runs import (
    CommandMetricAdapter,
    RepeatedRunPlan,
    collect_repeated_runs,
    load_repeated_run_plan,
    load_resume_bundle,
    write_replay_bundle,
)
from ragops.cli import main
from ragops.loader import ContractError
from ragops.models import MetricObservation, ReplayBundle, ReplayProvenance
from ragops.statistical import load_replay_bundle


FIXTURES = "scenarios/statistical_gate"


class FakeAdapter:
    def __init__(self) -> None:
        self.calls = []

    def collect(self, case_id, repeat_id):
        self.calls.append((case_id, repeat_id))
        return {"quality": 0.9}


def _plan(repeats=2):
    return RepeatedRunPlan(
        schema_version="0.1",
        scenario_id="scenario",
        scenario_digest="sha256:scenario",
        case_ids=("one", "two"),
        repeats=repeats,
        provenance=ReplayProvenance(
            dataset="dataset",
            evidence="evidence",
            evaluator="evaluator",
            application="application",
            model="model",
            model_config="config",
            environment="environment",
        ),
    )


def test_collects_in_stable_order_and_checkpoints() -> None:
    adapter = FakeAdapter()
    checkpoints = []

    bundle = collect_repeated_runs(_plan(), adapter, checkpoint=checkpoints.append)

    assert adapter.calls == [
        ("one", "run-0001"),
        ("two", "run-0001"),
        ("one", "run-0002"),
        ("two", "run-0002"),
    ]
    assert len(bundle.records) == 4
    assert [len(item.records) for item in checkpoints] == [1, 2, 3, 4]


def test_resume_skips_completed_observations(tmp_path) -> None:
    plan = _plan()
    partial = ReplayBundle(
        schema_version="0.1",
        scenario_id=plan.scenario_id,
        scenario_digest=plan.scenario_digest,
        provenance=plan.provenance,
        records=(MetricObservation("one", "run-0001", {"quality": 0.9}),),
    )
    output = tmp_path / "bundle.json"
    write_replay_bundle(output, partial)
    adapter = FakeAdapter()

    bundle = collect_repeated_runs(
        plan,
        adapter,
        existing=load_resume_bundle(output, resume=True),
    )

    assert len(bundle.records) == 4
    assert ("one", "run-0001") not in adapter.calls
    with pytest.raises(ContractError, match="pass --resume"):
        load_resume_bundle(output, resume=False)


def test_plan_and_resume_contracts_fail_closed(tmp_path) -> None:
    plan = load_repeated_run_plan(f"{FIXTURES}/run-plan.json")
    assert plan.repeats == 2
    bad = tmp_path / "bad.json"
    bad.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "scenario_id": "s",
                "scenario_digest": "d",
                "case_ids": ["duplicate", "duplicate"],
                "repeats": 1,
                "provenance": {
                    "dataset": "d",
                    "evidence": "r",
                    "evaluator": "e",
                    "application": "a",
                    "model": "m",
                    "model_config": "c",
                    "environment": "env",
                },
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ContractError, match="unique"):
        load_repeated_run_plan(bad)


def test_command_adapter_parses_bounded_metric_output(tmp_path) -> None:
    script = tmp_path / "metric.py"
    script.write_text('print("{\\"metrics\\": {\\"quality\\": 0.91}}")\n', encoding="utf-8")

    metrics = CommandMetricAdapter((sys.executable, str(script))).collect("one", "run-0001")

    assert metrics == {"quality": 0.91}


def test_collect_runs_cli_writes_resumable_bundle(monkeypatch, tmp_path) -> None:
    script = tmp_path / "metric.py"
    script.write_text('print("{\\"metrics\\": {\\"citation_precision\\": 0.94}}")\n', encoding="utf-8")
    output = tmp_path / "bundle.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "collect-runs",
            "--plan",
            f"{FIXTURES}/run-plan.json",
            "--output",
            str(output),
            "--command",
            sys.executable,
            str(script),
        ],
    )

    assert main() == 0
    assert len(load_replay_bundle(output).records) == 6

    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "collect-runs",
            "--plan",
            f"{FIXTURES}/run-plan.json",
            "--output",
            str(output),
            "--resume",
            "--command",
            sys.executable,
            str(script),
        ],
    )
    assert main() == 0


def test_collect_runs_cli_stops_after_sequential_pass(monkeypatch, tmp_path) -> None:
    script = tmp_path / "metric.py"
    script.write_text(
        'print("{\\"metrics\\": {\\"citation_precision\\": 0.945}}")\n',
        encoding="utf-8",
    )
    plan_data = json.loads(Path(f"{FIXTURES}/run-plan.json").read_text(encoding="utf-8"))
    plan_data["repeats"] = 5
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps(plan_data), encoding="utf-8")
    output = tmp_path / "bundle.json"
    decision = tmp_path / "decision.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "collect-runs",
            "--plan",
            str(plan),
            "--output",
            str(output),
            "--baseline-bundle",
            f"{FIXTURES}/baseline.json",
            "--sequential-policy",
            f"{FIXTURES}/sequential-policy.toml",
            "--sequential-report",
            str(decision),
            "--command",
            sys.executable,
            str(script),
        ],
    )

    assert main() == 0
    assert len(load_replay_bundle(output).records) == 6
    assert json.loads(decision.read_text(encoding="utf-8"))["decision"] == "pass"
