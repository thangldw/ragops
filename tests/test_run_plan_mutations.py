"""Malformed repeated-run plans and command output must fail with ContractError only."""

import copy
import json
import sys
from pathlib import Path

import pytest

from ragops.adapters.repeated_runs import (
    CommandMetricAdapter,
    load_repeated_run_plan,
    load_resume_bundle,
)
from ragops.loader import ContractError

PLAN = Path("scenarios/statistical_gate/run-plan.json")
BAD = ("bad", -1, 0, True, None, [], {}, 1e999, "x" * 5000)


def _paths(value, prefix=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield (*prefix, key)
            yield from _paths(child, (*prefix, key))


def _set(data: dict, path: tuple, value) -> dict:
    mutated = copy.deepcopy(data)
    target = mutated
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return mutated


def test_every_mutated_plan_field_fails_cleanly(tmp_path: Path) -> None:
    data = json.loads(PLAN.read_text(encoding="utf-8"))
    assert load_repeated_run_plan(PLAN).scenario_id == data["scenario_id"]
    target = tmp_path / "plan.json"
    rejected = 0
    for path in _paths(data):
        for value in BAD:
            target.write_text(json.dumps(_set(data, path, value)), encoding="utf-8")
            try:
                load_repeated_run_plan(target)
            except ContractError:
                rejected += 1
    removed = copy.deepcopy(data)
    for key in list(data):
        mutated = {k: v for k, v in removed.items() if k != key}
        target.write_text(json.dumps(mutated), encoding="utf-8")
        with pytest.raises(ContractError):
            load_repeated_run_plan(target)
    assert rejected > 30


@pytest.mark.parametrize("content", ["", "[]", "{", '{"schema_version": "0.1"}', "NaN"])
def test_unreadable_or_wrong_shape_plans_are_rejected(tmp_path: Path, content: str) -> None:
    target = tmp_path / "plan.json"
    target.write_text(content, encoding="utf-8")
    with pytest.raises(ContractError):
        load_repeated_run_plan(target)
    with pytest.raises(ContractError):
        load_repeated_run_plan(tmp_path / "missing.json")


def _script(tmp_path: Path, body: str) -> CommandMetricAdapter:
    path = tmp_path / "metric.py"
    path.write_text(body, encoding="utf-8")
    return CommandMetricAdapter((sys.executable, str(path)), timeout_seconds=10)


@pytest.mark.parametrize(
    "body",
    [
        "print('not json')",
        "print('[]')",
        "print('{\"metrics\": {}, \"extra\": 1}')",
        "print('{\"metrics\": {\"q\": \"high\"}}')",
        "print('{\"metrics\": {\"q\": NaN}}')",
        "import sys; sys.stderr.write('boom'); sys.exit(4)",
        "print('x' * 2_000_000_0)",
    ],
)
def test_command_output_contract(tmp_path: Path, body: str) -> None:
    with pytest.raises(ContractError):
        _script(tmp_path, body).collect("case", "run-1")


def test_command_receives_case_and_repeat_through_environment(tmp_path: Path) -> None:
    adapter = _script(
        tmp_path,
        "import os, json\nprint(json.dumps({'metrics': {'q': float(os.environ['RAGOPS_CASE_ID'] == 'c1' and os.environ['RAGOPS_REPEAT_ID'] == 'r1')}}))\n",
    )
    assert adapter.collect("c1", "r1") == {"q": 1.0}


def test_existing_output_requires_resume_and_symlinks_are_refused(tmp_path: Path) -> None:
    assert load_resume_bundle(tmp_path / "none.json", resume=True) is None
    existing = tmp_path / "bundle.json"
    existing.write_text(Path("scenarios/statistical_gate/baseline.json").read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ContractError, match="--resume"):
        load_resume_bundle(existing, resume=False)
    assert load_resume_bundle(existing, resume=True) is not None
    link = tmp_path / "link.json"
    link.symlink_to(existing)
    with pytest.raises(ContractError, match="symlink"):
        load_resume_bundle(link, resume=True)
