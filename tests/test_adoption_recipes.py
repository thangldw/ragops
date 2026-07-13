import re
from pathlib import Path


def test_gitlab_recipe_preserves_evidence_and_exit_code() -> None:
    recipe = Path("docs/examples/gitlab-ci-ragops.yml").read_text(encoding="utf-8")

    assert 'RAGOPS_VERSION: "2.3.0"' in recipe
    assert 'if: \'$CI_PIPELINE_SOURCE == "merge_request_event"\'' in recipe
    assert "gate_exit=$?" in recipe
    assert 'exit "$gate_exit"' in recipe
    assert "when: always" in recipe
    assert "ragops-report.md" in recipe
    assert "ragops-command.log" in recipe
    assert "allow_failure" not in recipe
    assert "PRIVATE-TOKEN" not in recipe


def test_downstream_github_publisher_is_copyable_and_least_privilege() -> None:
    recipe = Path("docs/examples/github-pr-comment.yml").read_text(encoding="utf-8")

    assert 'workflows: ["RAGOps"]' in recipe
    assert "RAGOPS_SOURCE_WORKFLOW: RAGOps" in recipe
    assert "actions: read" in recipe
    assert "contents: read" in recipe
    assert "pull-requests: write" in recipe
    assert "pull_request_target" not in recipe
    assert "persist-credentials: false" in recipe
    assert "repository: thangldw/ragops" in recipe
    assert re.search(r"ref: [0-9a-f]{40}", recipe)
    assert re.search(r"actions/checkout@[0-9a-f]{40}", recipe)
    assert "python .ragops-publisher/apps/github_pr_comment.py" in recipe


def test_pr_comment_design_keeps_write_path_separate() -> None:
    design = Path("docs/architecture/pr-comment-publishing.md").read_text(encoding="utf-8")
    adr = Path(
        "docs/architecture/adr/0014-separate-pr-evaluation-from-comment-publication.md"
    ).read_text(encoding="utf-8")

    for required in (
        "workflow_run",
        "pull-requests: write",
        "never `pull_request_target`",
        "do not checkout the pull request",
        "untrusted data",
        "<!-- ragops-release-gate -->",
    ):
        assert required in design
    assert "Accepted for bounded implementation" in adr
    assert "owner authorized" in adr
