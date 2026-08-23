import importlib.util
import json
import subprocess
import zipfile
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("local_release", Path("scripts/local_release.py"))
assert SPEC and SPEC.loader
local_release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(local_release)


def test_tag_must_match_package_version() -> None:
    assert local_release.assert_tag(local_release.milestone_tag()) == "v2.0.2"


def test_checksum_manifest_is_deterministic(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(local_release, "DIST", tmp_path)
    artifact = tmp_path / "artifact.whl"
    artifact.write_bytes(b"ragops")
    manifest = local_release.checksums([artifact])
    assert manifest.read_text().endswith("  artifact.whl\n")
    assert len(manifest.read_text().split()[0]) == 64
    local_release.verify_checksums(tmp_path)


def test_checksum_verification_rejects_tampering(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(local_release, "DIST", tmp_path)
    artifact = tmp_path / "artifact.whl"
    artifact.write_bytes(b"ragops")
    local_release.checksums([artifact])
    artifact.write_bytes(b"tampered")
    try:
        local_release.verify_checksums(tmp_path)
    except SystemExit as error:
        assert "checksum mismatch" in str(error)
    else:
        raise AssertionError("tampered artifact must be rejected")


def test_checksum_verification_rejects_path_traversal(tmp_path) -> None:
    (tmp_path / "SHA256SUMS").write_text(f"{'0' * 64}  ../outside.whl\n")
    try:
        local_release.verify_checksums(tmp_path)
    except SystemExit as error:
        assert "invalid checksum target" in str(error)
    else:
        raise AssertionError("checksum target must stay inside release directory")


def test_pypi_requires_explicit_token(monkeypatch) -> None:
    monkeypatch.delenv("PYPI_API_TOKEN", raising=False)
    try:
        local_release.pypi(local_release.milestone_tag(), True)
    except SystemExit as error:
        assert "PYPI_API_TOKEN" in str(error)
    else:
        raise AssertionError("publish must fail closed without a token")


def test_environment_tool_prefers_active_python_scripts_directory(tmp_path, monkeypatch) -> None:
    scripts = tmp_path / "bin"
    scripts.mkdir()
    python = scripts / "python"
    python.touch()
    ruff = scripts / "ruff"
    ruff.touch()
    monkeypatch.setattr(local_release.sys, "executable", str(python))

    assert local_release.environment_tool("ruff") == str(ruff)


def test_sbom_environment_uses_wheel_metadata_without_pip(tmp_path: Path) -> None:
    wheel = tmp_path / "ragops-2.0.2-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("ragops/__init__.py", "__version__ = '2.0.2'\n")
        archive.writestr(
            "ragops-2.0.2.dist-info/METADATA",
            "Metadata-Version: 2.1\nName: ragops\nVersion: 2.0.2\n",
        )

    python = local_release.prepare_sbom_environment(wheel, tmp_path / "sbom-venv")
    result = subprocess.run(
        [
            str(python),
            "-c",
            (
                "import importlib.metadata, importlib.util; "
                "print(importlib.metadata.version('ragops')); "
                "print(importlib.util.find_spec('pip') is None)"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.splitlines() == ["2.0.2", "True"]


def test_sbom_validation_rejects_local_build_paths(tmp_path: Path) -> None:
    sbom = tmp_path / "sbom.json"
    sbom.write_text(
        json.dumps(
            {
                "metadata": {
                    "component": {
                        "bom-ref": "root-component",
                        "name": "ragops",
                        "version": "2.0.2",
                        "externalReferences": [
                            {
                                "type": "distribution",
                                "url": "file:///private/build/ragops",
                            }
                        ],
                    }
                },
                "components": [],
                "dependencies": [{"ref": "root-component"}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="local file URL"):
        local_release.validate_sbom(sbom, "2.0.2")


def test_sbom_validation_rejects_wrong_root_version(tmp_path: Path) -> None:
    sbom = tmp_path / "sbom.json"
    sbom.write_text(
        json.dumps(
            {
                "metadata": {
                    "component": {
                        "bom-ref": "root-component",
                        "name": "ragops",
                        "version": "2.0.1",
                    }
                },
                "components": [],
                "dependencies": [{"ref": "root-component"}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="root component"):
        local_release.validate_sbom(sbom, "2.0.2")


def test_sbom_validation_accepts_dependency_free_release(tmp_path: Path) -> None:
    sbom = tmp_path / "sbom.json"
    sbom.write_text(
        json.dumps(
            {
                "metadata": {
                    "component": {
                        "bom-ref": "root-component",
                        "name": "ragops",
                        "version": "2.0.2",
                        "externalReferences": [
                            {"type": "website", "url": "https://github.com/thangldw/ragops"}
                        ],
                    }
                },
                "components": [],
                "dependencies": [{"ref": "root-component"}],
            }
        ),
        encoding="utf-8",
    )

    local_release.validate_sbom(sbom, "2.0.2")
