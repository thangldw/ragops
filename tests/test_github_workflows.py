import re
from pathlib import Path

WORKFLOW_ROOT = Path(".github/workflows")
EXPECTED = {"ragops-gate.yml", "ragops-statistical-gate.yml"}


def test_only_product_reusable_workflows_remain() -> None:
    assert {path.name for path in WORKFLOW_ROOT.glob("*.yml")} == EXPECTED


def test_reusable_workflows_are_read_only_manual_call_surfaces() -> None:
    for name in EXPECTED:
        workflow = (WORKFLOW_ROOT / name).read_text(encoding="utf-8")
        assert "workflow_call:" in workflow
        assert "contents: read" in workflow
        assert "pull_request_target" not in workflow
        assert "schedule:" not in workflow
        assert re.search(r"actions/checkout@[0-9a-f]{40}", workflow)
        assert re.search(r"actions/setup-python@[0-9a-f]{40}", workflow)
        assert "ragops-release-evidence" in workflow
        assert "ragops-report.html" in workflow


def test_current_operations_are_linked() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    for guide in (
        "docs/ARCHITECTURE.md",
        "docs/OPERATIONS.md",
        "docs/releases/v1.0.0.md",
    ):
        assert Path(guide).is_file()
        assert guide in readme
