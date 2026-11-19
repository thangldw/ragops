"""Every malformed policy must fail with ValueError, never crash with another error."""

import re
from pathlib import Path

import pytest

from ragops.config import (
    load_evaluation_policy,
    load_evaluator_drift_policy,
    load_regression_policy,
    load_sequential_policy,
    load_statistical_policy,
)

GATE = Path("scenarios/statistical_gate")
JA = Path("scenarios/japanese_troubleshooting")
CASES = (
    (load_statistical_policy, GATE / "policy.toml"),
    (load_evaluator_drift_policy, GATE / "drift-policy.toml"),
    (load_sequential_policy, GATE / "sequential-policy.toml"),
    (load_evaluation_policy, JA / "evaluation-policy.toml"),
)
BAD_VALUES = ('"bad"', "-1", "true", "1e999", "nan", "[]", "0", "2")
ASSIGNMENT = re.compile(r"^(?P<key>[A-Za-z_][\w.]*)\s*=\s*(?P<value>.+)$")


def _mutations(text: str):
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = ASSIGNMENT.match(line.strip())
        if not match:
            continue
        yield "\n".join(lines[:index] + lines[index + 1 :])
        for bad in BAD_VALUES:
            yield "\n".join([*lines[:index], f"{match['key']} = {bad}", *lines[index + 1 :]])
    yield text + "\nunexpected = 1\n"
    yield "[broken"
    yield ""


@pytest.mark.parametrize(("loader", "path"), CASES, ids=lambda value: getattr(value, "__name__", str(value)))
def test_valid_policy_loads_and_every_mutation_fails_cleanly(loader, path: Path, tmp_path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert loader(path) is not None

    target = tmp_path / "policy.toml"
    rejected = 0
    for mutated in _mutations(text):
        target.write_text(mutated, encoding="utf-8")
        try:
            loader(target)
        except ValueError:
            rejected += 1
    assert rejected >= 5


def test_regression_policy_rejects_negative_and_missing(tmp_path: Path) -> None:
    target = tmp_path / "regression.toml"
    base = Path("ragops.toml").read_text(encoding="utf-8")
    assert load_regression_policy("ragops.toml") is not None
    for mutated in (
        base.replace("0.05", "-0.05"),
        base.replace("0.0\n", "nan\n", 1),
        "[regression]\nunknown = 1\n",
        "",
        "[regression",
    ):
        target.write_text(mutated, encoding="utf-8")
        with pytest.raises(ValueError):
            load_regression_policy(target)
    with pytest.raises(ValueError):
        load_regression_policy(tmp_path / "missing.toml")
