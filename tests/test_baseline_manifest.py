import json
import shutil
import subprocess
from pathlib import Path

import pytest

from ragops.adapters.signing import sign_baseline_manifest, verify_baseline_signature
from ragops.baseline import (
    baseline_manifest_bytes,
    create_baseline_manifest,
    load_baseline_manifest,
    verify_baseline_manifest,
    write_baseline_manifest,
)
from ragops.cli import main
from ragops.loader import ContractError


FIXTURES = "scenarios/statistical_gate"


def test_baseline_manifest_is_deterministic_and_verifies(tmp_path) -> None:
    manifest = create_baseline_manifest(
        f"{FIXTURES}/baseline.json",
        f"{FIXTURES}/policy.toml",
        owner="thang",
        accepted_at="2026-07-15T21:00:00+09:00",
    )
    output = tmp_path / "baseline-manifest.json"
    write_baseline_manifest(output, manifest)

    loaded = load_baseline_manifest(output)
    verify_baseline_manifest(
        loaded,
        f"{FIXTURES}/baseline.json",
        f"{FIXTURES}/policy.toml",
    )
    assert baseline_manifest_bytes(loaded) == output.read_bytes()
    assert loaded.policy_kind == "statistical"


def test_baseline_manifest_rejects_changed_policy(tmp_path) -> None:
    manifest = create_baseline_manifest(
        f"{FIXTURES}/baseline.json",
        f"{FIXTURES}/policy.toml",
        owner="thang",
        accepted_at="2026-07-15T21:00:00+09:00",
    )
    changed = tmp_path / "policy.toml"
    changed.write_text(
        Path(f"{FIXTURES}/policy.toml").read_text(encoding="utf-8").replace(
            "minimum = 0.90", "minimum = 0.91"
        ),
        encoding="utf-8",
    )

    with pytest.raises(ContractError, match="digest or size"):
        verify_baseline_manifest(manifest, f"{FIXTURES}/baseline.json", changed)


@pytest.mark.skipif(shutil.which("ssh-keygen") is None, reason="ssh-keygen unavailable")
def test_ssh_signature_round_trip_and_tamper_rejection(tmp_path) -> None:
    manifest = create_baseline_manifest(
        f"{FIXTURES}/baseline.json",
        f"{FIXTURES}/policy.toml",
        owner="thang",
        accepted_at="2026-07-15T21:00:00+09:00",
    )
    manifest_path = tmp_path / "manifest.json"
    write_baseline_manifest(manifest_path, manifest)
    key = tmp_path / "signing-key"
    subprocess.run(
        ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)],
        check=True,
    )
    identity = "thang@ragops"
    allowed_signers = tmp_path / "allowed_signers"
    allowed_signers.write_text(
        f"{identity} {key.with_suffix('.pub').read_text(encoding='utf-8')}",
        encoding="utf-8",
    )
    signature = tmp_path / "manifest.sig"

    sign_baseline_manifest(manifest_path, key, signature)
    verify_baseline_signature(manifest_path, signature, allowed_signers, identity)

    manifest_path.write_bytes(manifest_path.read_bytes() + b" ")
    with pytest.raises(ContractError, match="verification failed"):
        verify_baseline_signature(manifest_path, signature, allowed_signers, identity)


def test_baseline_cli_create_and_verify(monkeypatch, tmp_path) -> None:
    manifest = tmp_path / "manifest.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "baseline-create",
            "--bundle",
            f"{FIXTURES}/baseline.json",
            "--policy",
            f"{FIXTURES}/policy.toml",
            "--owner",
            "thang",
            "--accepted-at",
            "2026-07-15T21:00:00+09:00",
            "--output",
            str(manifest),
        ],
    )
    assert main() == 0
    assert json.loads(manifest.read_text(encoding="utf-8"))["acceptance"]["owner"] == "thang"

    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "baseline-verify",
            "--manifest",
            str(manifest),
            "--bundle",
            f"{FIXTURES}/baseline.json",
            "--policy",
            f"{FIXTURES}/policy.toml",
        ],
    )
    assert main() == 0
