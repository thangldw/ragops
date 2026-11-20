import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("scripts").resolve()))

import release_tools as tools  # noqa: E402

COPIED = (
    "pyproject.toml", "README.md", "CHANGELOG.md", "action.yml", "src/ragops/__init__.py",
    ".kimi-plugin/plugin.json", "plugins/ragops/.claude-plugin/plugin.json", ".codex-plugin/plugin.json",
    "docs/examples/gitlab-ci-ragops.yml", "docs/examples/github-actions-ragops.yml",
    "docs/submission/DIRECTORY_SUBMISSION.md", "scripts/burned_versions.txt",
)


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    for relative in COPIED:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(relative, target)
    return tmp_path


def test_bump_updates_every_version_file_and_promotes_changelog(tree: Path) -> None:
    tools.current_version(tree)
    (tree / "CHANGELOG.md").write_text("# log\n\n## Unreleased\n\n- x\n", encoding="utf-8")

    changed = tools.bump("99.0.0", tree)

    assert tools.current_version(tree) == "99.0.0"
    for relative in (*tools.PLAIN_FILES, "README.md"):
        assert relative in changed
    assert "99.0.0" in (tree / "action.yml").read_text(encoding="utf-8")
    assert '__version__ = "99.0.0"' in (tree / "src/ragops/__init__.py").read_text(encoding="utf-8")
    assert "## [99.0.0] - " in (tree / "CHANGELOG.md").read_text(encoding="utf-8")
    assert (tree / "docs/releases/v99.0.0.md").is_file()
    assert tools.check("99.0.0", tree, offline=True) == []


@pytest.mark.parametrize("new", ["1.0.0", "not-a-version", "2.0.0", "2.2.0"])
def test_bump_refuses_old_invalid_and_burned_versions(tree: Path, new: str) -> None:
    with pytest.raises(tools.ReleaseError):
        tools.bump(new, tree)


def test_check_reports_every_problem_offline(tree: Path) -> None:
    problems = tools.check("2.2.0", tree, offline=True)
    text = " ".join(problems)
    assert "deleted" in text and "is missing" in text and "pyproject.toml version" in text


def test_the_real_repo_passes_offline_check_for_its_own_version() -> None:
    version = tools.current_version()
    assert tools.check(version, offline=True) == []
