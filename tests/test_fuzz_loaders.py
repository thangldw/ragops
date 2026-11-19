"""Property and tamper tests: malformed input must raise ContractError, never crash."""

import json
import random
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from ragops.adapters.otel_genai import otel_spans_to_trace_graph
from ragops.contracts import validate_contract
from ragops.evidence import create_evidence_bundle, verify_evidence_bundle
from ragops.loader import ContractError, responses_from_data, scenario_from_dict
from ragops.trace_graph import trace_graph_from_dict

JSON_VALUES = st.recursive(
    st.none()
    | st.booleans()
    | st.integers(-(10**6), 10**6)
    | st.floats(allow_nan=True, allow_infinity=True)
    | st.text(max_size=12),
    lambda children: st.lists(children, max_size=4)
    | st.dictionaries(st.text(max_size=8), children, max_size=5),
    max_leaves=12,
)
FUZZ = settings(max_examples=150, deadline=None, suppress_health_check=[HealthCheck.too_slow])
SCENARIO = json.loads(Path("scenarios/japanese_troubleshooting/scenario.json").read_text(encoding="utf-8"))
RESPONSES = json.loads(Path("scenarios/japanese_troubleshooting/sample_responses.json").read_text(encoding="utf-8"))


def _must_be_contract_error(function, value) -> None:
    try:
        function(value)
    except ContractError:
        pass


@pytest.mark.parametrize(
    "function",
    [scenario_from_dict, responses_from_data, trace_graph_from_dict, otel_spans_to_trace_graph, validate_contract],
    ids=lambda f: f.__name__,
)
@FUZZ
@given(value=JSON_VALUES)
def test_arbitrary_json_never_crashes_a_loader(function, value) -> None:
    _must_be_contract_error(function, value)


def _mutate(value, rng: random.Random):
    value = json.loads(json.dumps(value))
    junk = [None, "x", -1, [], {}, 1e999, True, 2**70]

    def walk(node):
        if isinstance(node, dict):
            for key in list(node):
                roll = rng.random()
                if roll < 0.1:
                    node[key] = rng.choice(junk)
                elif roll < 0.15:
                    del node[key]
                else:
                    walk(node[key])
        elif isinstance(node, list):
            for index in range(len(node)):
                if rng.random() < 0.1:
                    node[index] = rng.choice(junk)
                else:
                    walk(node[index])

    walk(value)
    return value


def test_mutated_real_fixtures_never_crash_loaders() -> None:
    rng = random.Random(20260719)
    for _ in range(1500):
        _must_be_contract_error(scenario_from_dict, _mutate(SCENARIO, rng))
        _must_be_contract_error(validate_contract, _mutate(SCENARIO, rng))
        mutated = _mutate({"items": RESPONSES}, rng).get("items")
        _must_be_contract_error(responses_from_data, mutated)


@pytest.fixture()
def bundle(tmp_path: Path) -> Path:
    artifact = tmp_path / "note.txt"
    artifact.write_text("evidence", encoding="utf-8")
    root = tmp_path / "bundle"
    create_evidence_bundle(
        root, {"note": artifact}, "PASS", ("synthetic",), "2026-01-01T00:00:00Z", {},
    )
    verify_evidence_bundle(root)
    return root


def _manifest(root: Path) -> dict:
    return json.loads((root / "manifest.json").read_text(encoding="utf-8"))


def _write(root: Path, data: dict) -> None:
    (root / "manifest.json").write_text(json.dumps(data), encoding="utf-8")


@pytest.mark.parametrize("path", ["../outside.txt", "/etc/passwd", "artifacts/../x", "artifacts/a/b", "other/note.txt", "artifacts/", ""])
def test_unsafe_artifact_paths_are_rejected(bundle: Path, path: str) -> None:
    data = _manifest(bundle)
    data["artifacts"][0]["path"] = path
    _write(bundle, data)
    with pytest.raises(ContractError):
        verify_evidence_bundle(bundle)


def test_symlink_and_undeclared_files_and_tampering_are_rejected(bundle: Path, tmp_path: Path) -> None:
    artifact = next((bundle / "artifacts").iterdir())
    original = artifact.read_bytes()

    artifact.write_bytes(original + b"!")
    with pytest.raises(ContractError, match="size|digest"):
        verify_evidence_bundle(bundle)
    artifact.write_bytes(b"X" * len(original))
    with pytest.raises(ContractError, match="digest"):
        verify_evidence_bundle(bundle)
    artifact.write_bytes(original)
    verify_evidence_bundle(bundle)

    (bundle / "artifacts" / "extra.txt").write_text("x", encoding="utf-8")
    with pytest.raises(ContractError, match="undeclared"):
        verify_evidence_bundle(bundle)
    (bundle / "artifacts" / "extra.txt").unlink()

    outside = tmp_path / "outside.txt"
    outside.write_text("x", encoding="utf-8")
    (bundle / "link.txt").symlink_to(outside)
    with pytest.raises(ContractError, match="symlink"):
        verify_evidence_bundle(bundle)
    (bundle / "link.txt").unlink()

    artifact.unlink()
    artifact.symlink_to(outside)
    with pytest.raises(ContractError):
        verify_evidence_bundle(bundle)


@FUZZ
@given(value=JSON_VALUES)
def test_arbitrary_manifest_content_is_rejected_cleanly(value, tmp_path_factory) -> None:
    root = tmp_path_factory.mktemp("manifest")
    (root / "manifest.json").write_text(json.dumps(value, allow_nan=True), encoding="utf-8")
    with pytest.raises(ContractError):
        verify_evidence_bundle(root)


def test_truncated_and_non_utf8_manifests_are_rejected(bundle: Path) -> None:
    text = (bundle / "manifest.json").read_bytes()
    for corrupted in (text[: len(text) // 2], b"\xff\xfe\x00", b"", b"null"):
        (bundle / "manifest.json").write_bytes(corrupted)
        with pytest.raises(ContractError):
            verify_evidence_bundle(bundle)
