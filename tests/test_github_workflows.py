from pathlib import Path

WORKFLOW_ROOT = Path(".github/workflows")


def test_repository_has_no_github_actions() -> None:
    assert not WORKFLOW_ROOT.exists() or not any(WORKFLOW_ROOT.iterdir())


def test_current_operations_are_linked() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    for guide in (
        "docs/ARCHITECTURE.md",
        "docs/OPERATIONS.md",
        "docs/releases/v1.0.0.md",
    ):
        assert Path(guide).is_file()
        assert guide in readme
