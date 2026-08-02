from pathlib import Path

WORKFLOW_ROOT = Path(".github/workflows")


def test_repository_only_has_release_publisher() -> None:
    assert sorted(path.name for path in WORKFLOW_ROOT.iterdir()) == ["publish-pypi.yml"]
    workflow = (WORKFLOW_ROOT / "publish-pypi.yml").read_text(encoding="utf-8")
    assert "id-token: write" in workflow
    assert "environment: pypi" in workflow
    assert "pull_request" not in workflow


def test_current_operations_are_linked() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    for guide in (
        "docs/ARCHITECTURE.md",
        "docs/OPERATIONS.md",
        "docs/releases/v1.2.0.md",
    ):
        assert Path(guide).is_file()
        assert guide in readme
