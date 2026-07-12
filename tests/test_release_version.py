from pathlib import Path
import tomllib

from ragops import __version__


def test_package_and_release_metadata_versions_match() -> None:
    metadata = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    version = metadata["project"]["version"]
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")
    release_notes = Path(f"docs/releases/v{version}.md")

    assert version == __version__
    assert f"## [{version}]" in changelog
    assert release_notes.is_file()
