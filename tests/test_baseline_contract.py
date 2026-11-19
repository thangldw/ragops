import json
from dataclasses import replace
from pathlib import Path

import pytest

from ragops.baseline import (
    create_baseline_manifest,
    load_baseline_manifest,
    verify_baseline_manifest,
    write_baseline_manifest,
)
from ragops.loader import ContractError

FIXTURES = Path("scenarios/statistical_gate")
BUNDLE = FIXTURES / "baseline.json"
POLICY = FIXTURES / "policy.toml"


def _manifest(**kwargs):
    arguments = {"owner": "owner", "accepted_at": "2026-07-15T21:00:00+09:00"}
    arguments.update(kwargs)
    return create_baseline_manifest(BUNDLE, POLICY, **arguments)


@pytest.mark.parametrize(
    "overrides",
    [
        {"owner": ""},
        {"accepted_at": "2026-07-15"},
        {"accepted_at": "2026-07-15T21:00:00"},
        {"accepted_at": "yesterday"},
    ],
)
def test_manifest_creation_rejects_bad_acceptance(overrides) -> None:
    with pytest.raises(ContractError):
        _manifest(**overrides)


def test_manifest_creation_rejects_missing_or_empty_inputs(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="Cannot read"):
        create_baseline_manifest(
            tmp_path / "nope.json", POLICY, owner="o", accepted_at="2026-07-15T21:00:00Z"
        )
    empty = tmp_path / "empty.toml"
    empty.write_bytes(b"")
    with pytest.raises(ContractError, match="between 1 and"):
        create_baseline_manifest(BUNDLE, empty, owner="o", accepted_at="2026-07-15T21:00:00Z")


def test_loader_rejects_non_object_unknown_fields_and_bad_json(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    for content, message in (
        ("not json", "Cannot load"),
        ("[]", "must be an object"),
        ('{"schema_version": "0.1"}', "do not match schema"),
    ):
        path.write_text(content, encoding="utf-8")
        with pytest.raises(ContractError, match=message):
            load_baseline_manifest(path)


def test_verify_rejects_tampered_bundle_and_metadata(tmp_path: Path) -> None:
    manifest = _manifest()
    tampered = tmp_path / "baseline.json"
    tampered.write_bytes(BUNDLE.read_bytes() + b" ")
    with pytest.raises(ContractError, match="bundle digest or size"):
        verify_baseline_manifest(manifest, tampered, POLICY)

    other_scenario = replace(manifest, scenario_id="someone-else")
    with pytest.raises(ContractError, match="metadata does not match"):
        verify_baseline_manifest(other_scenario, BUNDLE, POLICY)

    other_kind = replace(manifest, policy_kind="sequential")
    with pytest.raises(ContractError, match="policy kind"):
        verify_baseline_manifest(other_kind, BUNDLE, POLICY)


def test_verify_rejects_invalid_manifest_values() -> None:
    manifest = _manifest()
    for broken in (
        replace(manifest, schema_version="9.9"),
        replace(manifest, policy_kind="other"),
        replace(manifest, bundle=replace(manifest.bundle, sha256="ABC")),
        replace(manifest, bundle=replace(manifest.bundle, bytes=0)),
        replace(manifest, bundle=replace(manifest.bundle, bytes="12")),
    ):
        with pytest.raises(ContractError):
            verify_baseline_manifest(broken, BUNDLE, POLICY)


def test_write_refuses_symlink_output(tmp_path: Path) -> None:
    target = tmp_path / "real.json"
    target.write_text("{}", encoding="utf-8")
    link = tmp_path / "link.json"
    link.symlink_to(target)
    with pytest.raises(ContractError, match="symlink"):
        write_baseline_manifest(link, _manifest())
    assert json.loads(target.read_text(encoding="utf-8")) == {}
