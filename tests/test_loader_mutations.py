"""Systematically corrupt valid inputs: loaders may reject them, but only with their own error type."""

import copy
import json
import re
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest

from ragops.config import (
    load_evaluator_drift_policy,
    load_sequential_policy,
    load_statistical_policy,
)
from ragops.datasets import create_dataset_manifest, load_dataset_manifest, write_dataset_manifest
from ragops.evidence import create_evidence_bundle, load_evidence_manifest
from ragops.loader import ContractError
from ragops.pilot import (
    PilotContractError,
    load_pilot_economics,
    load_pilot_manifest,
    load_pilot_observations,
)

JUNK = (None, "x", "", -1, 0, 1e999, True, False, [], {}, [1], {"k": 1}, 2**70)
ALLOWED = (ContractError, PilotContractError, ValueError)  # config loaders raise plain ValueError
FIXTURES = Path("docs/gtm/pilot-fixtures")


def _paths(node: Any, prefix: tuple = ()) -> Iterator[tuple]:
    yield prefix
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _paths(value, (*prefix, key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _paths(value, (*prefix, index))


def _mutants(valid: Any) -> Iterator[Any]:
    for path in _paths(valid):
        if not path:
            continue
        for replacement in (*JUNK, ...):
            clone = copy.deepcopy(valid)
            parent = clone
            for step in path[:-1]:
                parent = parent[step]
            if replacement is ...:
                if isinstance(parent, dict):
                    del parent[path[-1]]
                else:
                    parent.pop(path[-1])
            else:
                parent[path[-1]] = replacement
            yield clone


def _exercise(valid: Any, write: Callable[[Any], Path], load: Callable[[Path], Any]) -> int:
    rejected = 0
    load(write(valid))
    for mutant in _mutants(valid):
        try:
            load(write(mutant))
        except ALLOWED:
            rejected += 1
    return rejected


def _json_writer(path: Path) -> Callable[[Any], Path]:
    def write(data: Any) -> Path:
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    return write


def test_pilot_manifest_and_economics_mutations(tmp_path: Path) -> None:
    manifest = json.loads((FIXTURES / "synthetic-manifest.json").read_text(encoding="utf-8"))
    economics = json.loads((FIXTURES / "synthetic-economics.json").read_text(encoding="utf-8"))
    assert _exercise(manifest, _json_writer(tmp_path / "m.json"), load_pilot_manifest) > 20
    assert _exercise(economics, _json_writer(tmp_path / "e.json"), load_pilot_economics) > 10


def test_pilot_observation_mutations(tmp_path: Path) -> None:
    lines = (FIXTURES / "synthetic-observations.jsonl").read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    path = tmp_path / "o.jsonl"

    def write(record: Any) -> Path:
        path.write_text(json.dumps(record) + "\n", encoding="utf-8")
        return path

    assert _exercise(first, write, load_pilot_observations) > 20
    path.write_text("{not json}\n", encoding="utf-8")
    with pytest.raises(PilotContractError):
        load_pilot_observations(path)


def test_dataset_manifest_mutations(tmp_path: Path) -> None:
    case = {
        "id": "a", "question": "Reset password", "evidence": ["Use the portal."],
        "required_citation_ids": ["p1"], "category": "policy", "severity": "high",
        "language": "en", "tags": ["x"], "source": "export", "reviewed": True,
    }
    manifest = create_dataset_manifest(
        "support", "1.0", (case,), splits={"train": ("a",)},
        source_classification="production-derived", owners=("team",),
    )
    source = tmp_path / "d.json"
    write_dataset_manifest(source, manifest)
    valid = json.loads(source.read_text(encoding="utf-8"))
    assert _exercise(valid, _json_writer(tmp_path / "m.json"), load_dataset_manifest) > 20


def test_evidence_manifest_mutations(tmp_path: Path) -> None:
    artifact = tmp_path / "a.txt"
    artifact.write_text("evidence", encoding="utf-8")
    bundle = tmp_path / "bundle"
    create_evidence_bundle(bundle, {"a": artifact}, "PASS", ("synthetic",), "2026-01-01T00:00:00Z", {"k": "v"})
    valid = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    assert _exercise(valid, _json_writer(tmp_path / "manifest.json"), load_evidence_manifest) > 20


ASSIGNMENT = re.compile(r"^(?P<key>[A-Za-z_]\w*)\s*=\s*(?P<value>.+)$")
BAD = ('"bad"', "-1", "true", "1e999", "nan", "[]", "{}", "0", '""', "[1]", "1000000", "1.5")


def _toml_mutants(text: str) -> Iterator[str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = ASSIGNMENT.match(line.strip())
        if not match:
            continue
        yield "\n".join(lines[:index] + lines[index + 1 :])
        for bad in BAD:
            yield "\n".join([*lines[:index], f"{match['key']} = {bad}", *lines[index + 1 :]])
    yield text + "\n[unknown]\nx = 1\n"
    yield "[broken"


@pytest.mark.parametrize(
    ("name", "loader"),
    [("policy.toml", load_statistical_policy), ("drift-policy.toml", load_evaluator_drift_policy),
     ("sequential-policy.toml", load_sequential_policy)],
)
def test_statistical_policy_mutations(tmp_path: Path, name: str, loader: Callable[[Path], Any]) -> None:
    text = Path("scenarios/statistical_gate", name).read_text(encoding="utf-8")
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    loader(path)
    rejected = 0
    for mutant in _toml_mutants(text):
        path.write_text(mutant, encoding="utf-8")
        try:
            loader(path)
        except ALLOWED:
            rejected += 1
    assert rejected >= 10


def test_replay_bundle_mutations_through_compare_and_sequential(tmp_path: Path) -> None:
    from ragops.sequential import compare_replay_bundles_sequentially
    from ragops.statistical import compare_replay_bundles, replay_bundle_from_dict

    base = json.loads(Path("scenarios/statistical_gate/baseline.json").read_text(encoding="utf-8"))
    cand = json.loads(Path("scenarios/statistical_gate/candidate-pass.json").read_text(encoding="utf-8"))
    stat_policy = load_statistical_policy("scenarios/statistical_gate/policy.toml")
    seq_policy = load_sequential_policy("scenarios/statistical_gate/sequential-policy.toml")
    good_base = replay_bundle_from_dict(base)
    good_cand = replay_bundle_from_dict(cand)
    compare_replay_bundles(good_base, good_cand, stat_policy)
    rejected = 0
    for mutant in _mutants(cand):
        try:
            candidate = replay_bundle_from_dict(mutant)
            compare_replay_bundles(good_base, candidate, stat_policy)
            compare_replay_bundles_sequentially(good_base, candidate, seq_policy)
        except ALLOWED:
            rejected += 1
    assert rejected > 20


def test_calibration_set_mutations(tmp_path: Path) -> None:
    from ragops.calibration import load_calibration_set

    sets = sorted(Path("benchmarks").rglob("*calibration*.json"))
    if not sets:
        pytest.skip("no calibration fixture shipped")
    valid = json.loads(sets[0].read_text(encoding="utf-8"))
    assert _exercise(valid, _json_writer(tmp_path / "c.json"), load_calibration_set) > 5


def test_trace_graph_and_expectation_mutations(tmp_path: Path) -> None:
    from ragops.trace_graph import load_trace_expectation, load_trace_graph
    from tests.test_trace_graph import _tool_trace

    expectation = {
        "expected_tools": [{"name": "lookup_order", "arguments": {"order_id": "ORD-1"}}],
        "expected_document_ids": ["policy-1"],
        "maximum_steps": 3,
    }
    assert _exercise(_tool_trace(), _json_writer(tmp_path / "t.json"), load_trace_graph) > 30
    assert _exercise(expectation, _json_writer(tmp_path / "e.json"), load_trace_expectation) > 8
