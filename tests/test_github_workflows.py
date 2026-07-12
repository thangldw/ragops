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
    assert workflow.count("if: always()") == 3
    assert "$GITHUB_STEP_SUMMARY" in workflow


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
    assert "ragops-version: v1.5.0" in workflow
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
