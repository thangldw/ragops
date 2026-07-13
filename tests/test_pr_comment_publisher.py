import io
import json
import stat
import zipfile

import pytest

import apps.github_pr_comment as publisher
from apps.github_pr_comment import (
    MARKER,
    PublisherContractError,
    build_comment,
    marker_comment_id,
    read_evidence_archive,
    select_artifact,
    validate_source_event,
    validate_artifact_redirect_url,
)

REPOSITORY = "thangldw/ragops"
WORKFLOW = "RAGOps reusable gate smoke"
HEAD_SHA = "a" * 40


def source_event(*, conclusion: str = "failure", pull_requests: list | None = None) -> dict:
    return {
        "action": "completed",
        "repository": {"full_name": REPOSITORY},
        "workflow_run": {
            "id": 123,
            "name": WORKFLOW,
            "event": "pull_request",
            "status": "completed",
            "conclusion": conclusion,
            "head_sha": HEAD_SHA,
            "html_url": f"https://github.com/{REPOSITORY}/actions/runs/123",
            "repository": {"full_name": REPOSITORY},
            "pull_requests": [{"number": 7}] if pull_requests is None else pull_requests,
        },
    }


def evidence_archive(*, gate_exit_code: int = 2, extra_file: bool = False) -> bytes:
    manifest = {
        "schema_version": "ragops-github-evidence-0.1",
        "repository": REPOSITORY,
        "event_name": "pull_request",
        "workflow": WORKFLOW,
        "run_id": 123,
        "head_sha": HEAD_SHA,
        "pull_request_number": 7,
        "gate_exit_code": gate_exit_code,
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as bundle:
        bundle.writestr("ragops-report.md", "# Result\n\nRelease blocked.\n")
        bundle.writestr("ragops-command.log", "exit 2\n")
        bundle.writestr("ragops-evidence.json", json.dumps(manifest))
        if extra_file:
            bundle.writestr("unexpected.sh", "echo unsafe")
    return output.getvalue()


def test_validated_blocked_evidence_builds_bounded_comment() -> None:
    source = validate_source_event(
        source_event(), expected_repository=REPOSITORY, expected_workflow=WORKFLOW
    )
    report = read_evidence_archive(evidence_archive(), source)
    comment = build_comment(report, source)

    assert comment.startswith(MARKER)
    assert "RAGOps release gate: BLOCK" in comment
    assert "actions/runs/123" in comment


def test_source_event_rejects_ambiguous_pr_association() -> None:
    with pytest.raises(PublisherContractError, match="exactly one PR"):
        validate_source_event(
            source_event(pull_requests=[]),
            expected_repository=REPOSITORY,
            expected_workflow=WORKFLOW,
        )


def test_source_event_accepts_single_fork_pr_association() -> None:
    payload = source_event()
    payload["workflow_run"]["head_repository"] = {"full_name": "contributor/ragops"}
    payload["workflow_run"]["head_branch"] = "publisher-fixture"

    source = validate_source_event(
        payload,
        expected_repository=REPOSITORY,
        expected_workflow=WORKFLOW,
    )

    assert source.repository == REPOSITORY
    assert source.pull_request_number == 7


def test_artifact_selection_is_exact_and_bounded() -> None:
    artifact = select_artifact(
        {
            "total_count": 1,
            "artifacts": [
                {
                    "name": "ragops-release-evidence",
                    "expired": False,
                    "size_in_bytes": 100,
                    "archive_download_url": "https://api.github.com/artifacts/1/zip",
                }
            ]
        }
    )
    assert artifact["size_in_bytes"] == 100

    with pytest.raises(PublisherContractError, match="exactly one"):
        select_artifact({"total_count": 0, "artifacts": []})


def test_artifact_selection_rejects_expired_or_paginated_results() -> None:
    expired = {
        "total_count": 1,
        "artifacts": [
            {
                "name": "ragops-release-evidence",
                "expired": True,
                "size_in_bytes": 100,
                "archive_download_url": "https://api.github.com/artifacts/1/zip",
            }
        ],
    }
    with pytest.raises(PublisherContractError, match="expired"):
        select_artifact(expired)

    first_hundred = [
        {
            "name": f"unrelated-{index}",
            "expired": False,
            "size_in_bytes": 100,
            "archive_download_url": f"https://api.github.com/artifacts/{index}/zip",
        }
        for index in range(100)
    ]
    with pytest.raises(PublisherContractError, match="incomplete or paginated"):
        select_artifact({"total_count": 101, "artifacts": first_hundred})


def test_archive_rejects_unexpected_or_non_regular_files() -> None:
    source = validate_source_event(
        source_event(), expected_repository=REPOSITORY, expected_workflow=WORKFLOW
    )
    with pytest.raises(PublisherContractError, match="allowlist"):
        read_evidence_archive(evidence_archive(extra_file=True), source)

    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as bundle:
        for name, value in (
            ("ragops-report.md", "report"),
            ("ragops-command.log", "log"),
            ("ragops-evidence.json", "{}"),
        ):
            info = zipfile.ZipInfo(name)
            if name == "ragops-command.log":
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
            bundle.writestr(info, value)
    with pytest.raises(PublisherContractError, match="non-regular"):
        read_evidence_archive(output.getvalue(), source)


def test_archive_rejects_manifest_or_conclusion_mismatch() -> None:
    blocked_source = validate_source_event(
        source_event(), expected_repository=REPOSITORY, expected_workflow=WORKFLOW
    )
    with pytest.raises(PublisherContractError, match="conclusion"):
        read_evidence_archive(evidence_archive(gate_exit_code=0), blocked_source)


def test_marker_comment_update_is_idempotent_and_ambiguous_state_fails() -> None:
    comment = {
        "id": 99,
        "body": f"{MARKER}\nold",
        "user": {"type": "Bot", "login": "github-actions[bot]"},
    }
    assert marker_comment_id([comment]) == 99
    assert marker_comment_id([]) is None
    with pytest.raises(PublisherContractError, match="multiple"):
        marker_comment_id([comment, {**comment, "id": 100}])


def test_artifact_redirect_never_sends_token_to_arbitrary_host() -> None:
    validate_artifact_redirect_url("https://productionresults.blob.core.windows.net/path?signed=1")
    with pytest.raises(PublisherContractError, match="approved HTTPS storage host"):
        validate_artifact_redirect_url("https://attacker.example/artifact.zip")
    with pytest.raises(PublisherContractError, match="approved HTTPS storage host"):
        validate_artifact_redirect_url("http://objects.githubusercontent.com/artifact.zip")


def test_comment_pagination_fails_closed_after_one_thousand_comments(monkeypatch) -> None:
    client = publisher.GitHubClient("token")
    requested_urls = []

    def full_page(url: str, *, method: str = "GET", body=None):
        assert method == "GET"
        assert body is None
        requested_urls.append(url)
        return [
            {"id": index, "body": "unrelated", "user": {"type": "User"}}
            for index in range(100)
        ]

    monkeypatch.setattr(client, "request_json", full_page)

    with pytest.raises(PublisherContractError, match="safe page limit"):
        client.request_list_pages("https://api.github.com/repos/thangldw/ragops/issues/7/comments")

    assert len(requested_urls) == 10
    assert requested_urls[-1].endswith("per_page=100&page=10")


@pytest.mark.parametrize("http_status", [403, 429])
def test_github_rate_limit_response_fails_closed(monkeypatch, http_status: int) -> None:
    def rate_limited(request, timeout: int = 30):
        raise publisher.urllib.error.HTTPError(
            request.full_url,
            http_status,
            "rate limited",
            hdrs={},
            fp=None,
        )

    monkeypatch.setattr(publisher.urllib.request, "urlopen", rate_limited)
    client = publisher.GitHubClient("token")

    with pytest.raises(PublisherContractError, match="GitHub API request failed"):
        client.request_json("https://api.github.com/rate_limit")


def test_publish_comment_creates_one_comment_through_json_api(monkeypatch, tmp_path) -> None:
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps(source_event()), encoding="utf-8")
    calls = []

    class FakeClient:
        def __init__(self, token: str) -> None:
            assert token == "token"

        def request_json(self, url: str, *, method: str = "GET", body=None):
            calls.append((method, url, body))
            if "/artifacts?" in url:
                return {
                    "total_count": 1,
                    "artifacts": [
                        {
                            "name": "ragops-release-evidence",
                            "expired": False,
                            "size_in_bytes": 500,
                            "archive_download_url": (
                                f"https://api.github.com/repos/{REPOSITORY}/actions/artifacts/9/zip"
                            ),
                        }
                    ],
                }
            return {"id": 55}

        def request_bytes(self, url: str) -> bytes:
            assert url.endswith("/actions/artifacts/9/zip")
            return evidence_archive()

        def request_list_pages(self, url: str):
            assert url.endswith("/issues/7/comments")
            return []

    monkeypatch.setattr(publisher, "GitHubClient", FakeClient)

    outcome = publisher.publish_comment(
        event_path=event_path,
        repository=REPOSITORY,
        workflow=WORKFLOW,
        token="token",
    )

    assert outcome == "created"
    post = calls[-1]
    assert post[0] == "POST"
    assert post[1].endswith("/issues/7/comments")
    assert post[2]["body"].startswith(MARKER)
