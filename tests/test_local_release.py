import importlib.util
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("local_release", Path("scripts/local_release.py"))
assert SPEC and SPEC.loader
local_release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(local_release)


def test_tag_must_match_package_version() -> None:
    assert local_release.assert_tag(f"v{local_release.version()}") == f"v{local_release.version()}"


def test_checksum_manifest_is_deterministic(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(local_release, "DIST", tmp_path)
    artifact = tmp_path / "artifact.whl"
    artifact.write_bytes(b"ragops")
    manifest = local_release.checksums([artifact])
    assert manifest.read_text().endswith("  artifact.whl\n")
    assert len(manifest.read_text().split()[0]) == 64


def test_pypi_requires_explicit_token(monkeypatch) -> None:
    monkeypatch.delenv("PYPI_API_TOKEN", raising=False)
    try:
        local_release.pypi(f"v{local_release.version()}", True)
    except SystemExit as error:
        assert "PYPI_API_TOKEN" in str(error)
    else:
        raise AssertionError("publish must fail closed without a token")
