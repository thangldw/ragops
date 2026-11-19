"""Malformed release policy v2 files must fail with ContractError, never another exception."""

import re
from pathlib import Path

import pytest

from ragops.loader import ContractError
from ragops.policy_v2 import load_release_policy_v2

VALID = """
[release]
minimum_cases = 1
insufficient_evidence = "block"

[metrics.citation_coverage]
direction = "higher"
minimum = 0.9
max_regression = 0.05
severity = "block"

[metrics.latency_ms]
direction = "lower"
maximum = 1000
severity = "warn"

[[slices]]
name = "japanese"
language = "ja"
tags = ["abstain"]
minimum_cases = 2

[tails.latency_ms]
percentile = 0.95
maximum = 2000
severity = "block"

[[waivers]]
gate_id = "global:latency_ms:maximum"
owner = "ml-platform"
reason = "migration window"
issued_at = "2026-01-01T00:00:00Z"
expires_at = "2026-02-01T00:00:00Z"
""".strip()

ASSIGNMENT = re.compile(r"^(?P<key>[A-Za-z_]\w*)\s*=\s*(?P<value>.+)$")
BAD_VALUES = ('"bad"', "-1", "true", "1e999", "nan", "[]", "{}", "0", '""', "[1]", "1000000")


def _mutations(text: str):
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = ASSIGNMENT.match(line.strip())
        if not match:
            continue
        yield "\n".join(lines[:index] + lines[index + 1 :])
        for bad in BAD_VALUES:
            yield "\n".join([*lines[:index], f"{match['key']} = {bad}", *lines[index + 1 :]])
    yield text + "\n[unknown]\nx = 1\n"
    yield text.replace("[[slices]]", "[slices]").replace("[[waivers]]", "[waivers]")
    yield text.replace("[tails.latency_ms]", "tails = 1\n[x]")
    yield "[broken"


def test_valid_policy_loads(tmp_path: Path) -> None:
    path = tmp_path / "policy.toml"
    path.write_text(VALID, encoding="utf-8")
    policy = load_release_policy_v2(path)
    assert len(policy.metrics) == 2 and len(policy.slices) == 1 and len(policy.waivers) == 1


def test_every_mutation_fails_with_contract_error_or_loads(tmp_path: Path) -> None:
    path = tmp_path / "policy.toml"
    rejected = 0
    for mutated in _mutations(VALID):
        path.write_text(mutated, encoding="utf-8")
        try:
            load_release_policy_v2(path)
        except ContractError:
            rejected += 1
    assert rejected >= 40


def test_missing_file_is_a_contract_error(tmp_path: Path) -> None:
    with pytest.raises(ContractError):
        load_release_policy_v2(tmp_path / "missing.toml")
