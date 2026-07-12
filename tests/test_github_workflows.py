import re
from pathlib import Path


def test_reusable_pr_gate_is_read_only_and_preserves_evidence() -> None:
    workflow = Path(".github/workflows/ragops-gate.yml").read_text(encoding="utf-8")

    assert "workflow_call:" in workflow
    assert "contents: read" in workflow
    assert "pull_request_target" not in workflow
    assert "RAGOPS_SCENARIO: ${{ inputs.scenario }}" in workflow
    assert '"$RAGOPS_SCENARIO"' in workflow
    assert "ragops-release-evidence" in workflow
    assert workflow.count("if: always()") == 4
    assert "$GITHUB_STEP_SUMMARY" in workflow
    assert "ragops-evidence.json" in workflow
    assert "ragops-github-evidence-0.1" in workflow
    for action in ("actions/checkout", "actions/setup-python", "actions/upload-artifact"):
        assert re.search(rf"{action}@[0-9a-f]{{40}}", workflow)


def test_pr_comment_publisher_is_isolated_bounded_and_commit_pinned() -> None:
    workflow = Path(".github/workflows/ragops-pr-comment.yml").read_text(encoding="utf-8")

    assert "workflow_run:" in workflow
    assert 'workflows: ["RAGOps reusable gate smoke"]' in workflow
    assert "actions: read" in workflow
    assert "contents: read" in workflow
    assert "pull-requests: write" in workflow
    assert "pull_request_target" not in workflow
    assert "download-artifact" not in workflow
    assert re.search(r"actions/checkout@[0-9a-f]{40}", workflow)
    assert "persist-credentials: false" in workflow
    assert "python apps/github_pr_comment.py" in workflow


def test_pypi_workflow_is_manual_oidc_and_commit_pinned() -> None:
    workflow = Path(".github/workflows/publish-pypi.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "environment: pypi" in workflow
    assert "id-token: write" in workflow
    assert "tag {tag!r} does not match package version" in workflow
    assert "@release/v1" not in workflow
    assert re.search(r"pypa/gh-action-pypi-publish@[0-9a-f]{40}", workflow)


def test_repository_smoke_calls_the_reusable_gate() -> None:
    workflow = Path(".github/workflows/ragops-gate-smoke.yml").read_text(encoding="utf-8")

    assert "uses: ./.github/workflows/ragops-gate.yml" in workflow
    assert "ragops-version: v1.7.0" in workflow
    assert "benchmark-baseline.json" in workflow


def test_integration_guides_are_linked_from_readme() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    guides = (
        "docs/engineering/github-pr-gate.md",
        "docs/engineering/export-your-first-trace.md",
        "docs/engineering/pypi-publishing.md",
    )

    for guide in guides:
        assert Path(guide).is_file()
        assert guide in readme
