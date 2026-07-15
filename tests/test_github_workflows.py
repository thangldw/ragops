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
    assert "RAGOps reusable gate smoke" in workflow
    assert "RAGOps statistical gate smoke" in workflow
    assert "actions: read" in workflow
    assert "contents: read" in workflow
    assert "pull-requests: write" in workflow
    assert "pull_request_target" not in workflow
    assert "download-artifact" not in workflow
    assert re.search(r"actions/checkout@[0-9a-f]{40}", workflow)
    assert "persist-credentials: false" in workflow
    assert "python apps/github_pr_comment.py" in workflow


def test_reusable_statistical_gate_is_read_only_bounded_and_commit_pinned() -> None:
    workflow = Path(".github/workflows/ragops-statistical-gate.yml").read_text(
        encoding="utf-8"
    )

    assert "workflow_call:" in workflow
    assert "contents: read" in workflow
    assert "pull_request_target" not in workflow
    assert "compare-runs" in workflow
    assert "compare-sequential" in workflow
    assert "baseline-verify" in workflow
    assert "ragops-release-evidence" in workflow
    assert "ragops-github-evidence-0.1" in workflow
    assert workflow.count("if: always()") == 4
    for action in ("actions/checkout", "actions/setup-python", "actions/upload-artifact"):
        assert re.search(rf"{action}@[0-9a-f]{{40}}", workflow)


def test_statistical_smoke_calls_reusable_gate_with_recorded_fixtures() -> None:
    workflow = Path(".github/workflows/ragops-statistical-gate-smoke.yml").read_text(
        encoding="utf-8"
    )

    assert "uses: ./.github/workflows/ragops-statistical-gate.yml" in workflow
    assert "ragops-version: ${{ github.event.pull_request.head.sha || github.sha }}" in workflow
    assert "scenarios/statistical_gate/baseline.json" in workflow
    assert "scenarios/statistical_gate/candidate-pass.json" in workflow


def test_pypi_workflow_is_manual_oidc_and_commit_pinned() -> None:
    workflow = Path(".github/workflows/publish-pypi.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "environment: pypi" in workflow
    assert "id-token: write" in workflow
    assert "tag {tag!r} does not match package version" in workflow
    assert "@release/v1" not in workflow
    assert re.search(r"pypa/gh-action-pypi-publish@[0-9a-f]{40}", workflow)
    assert "gh release download" in workflow
    assert "sha256sum --check SHA256SUMS" in workflow
    assert "python -m build" not in workflow


def test_release_builds_once_with_sbom_checksums_and_provenance() -> None:
    workflow = Path(".github/workflows/release.yml").read_text(encoding="utf-8")

    assert workflow.count("python -m build") == 1
    assert "cyclonedx-bom==7.3.0" in workflow
    assert "--output-reproducible" in workflow
    assert "SHA256SUMS" in workflow
    assert re.search(r"actions/attest-build-provenance@[0-9a-f]{40}", workflow)
    for action in ("actions/checkout", "actions/setup-python", "actions/upload-artifact"):
        assert re.search(rf"{action}@[0-9a-f]{{40}}", workflow)


def test_repository_smoke_calls_the_reusable_gate() -> None:
    workflow = Path(".github/workflows/ragops-gate-smoke.yml").read_text(encoding="utf-8")

    assert "uses: ./.github/workflows/ragops-gate.yml" in workflow
    assert "ragops-version: ${{ github.event.pull_request.head.sha || github.sha }}" in workflow
    assert "benchmark-baseline.json" in workflow


def test_ci_covers_every_declared_python_minor() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    for version in ("3.11", "3.12", "3.13"):
        assert f'"{version}"' in workflow


def test_integration_guides_are_linked_from_readme() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    guides = (
        "docs/engineering/ci-gates.md",
        "docs/engineering/integrations.md",
        "docs/engineering/testing-and-release.md",
    )

    for guide in guides:
        assert Path(guide).is_file()
        assert guide in readme


def test_pages_deploys_site_from_main_with_pinned_actions() -> None:
    workflow = Path(".github/workflows/pages.yml").read_text(encoding="utf-8")

    assert "branches: [main]" in workflow
    assert "path: site" in workflow
    for action in (
        "actions/checkout",
        "actions/configure-pages",
        "actions/upload-pages-artifact",
        "actions/deploy-pages",
    ):
        assert re.search(rf"{action}@[0-9a-f]{{40}}", workflow)
