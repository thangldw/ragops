from __future__ import annotations

import io
import json
import os
import re
import stat
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ARTIFACT_NAME = "ragops-release-evidence"
MARKER = "<!-- ragops-release-gate -->"
REQUIRED_FILES = frozenset({"ragops-report.md", "ragops-command.log", "ragops-evidence.json"})
OPTIONAL_FILES = frozenset({"ragops-report.html"})
MAX_ARCHIVE_BYTES = 256_000
MAX_TOTAL_UNCOMPRESSED_BYTES = 128_000
MAX_REPORT_BYTES = 55_000
MAX_MANIFEST_BYTES = 4_096
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class PublisherContractError(ValueError):
    """Raised when workflow or artifact evidence crosses the trust boundary."""


@dataclass(frozen=True)
class SourceRun:
    repository: str
    workflow: str
    run_id: int
    head_sha: str
    pull_request_number: int
    conclusion: str
    html_url: str


def validate_source_event(
    payload: dict[str, Any], *, expected_repository: str, expected_workflow: str
) -> SourceRun:
    if payload.get("action") != "completed":
        raise PublisherContractError("workflow_run action must be completed")
    repository = payload.get("repository") or {}
    workflow_run = payload.get("workflow_run") or {}
    if repository.get("full_name") != expected_repository:
        raise PublisherContractError("event repository does not match GITHUB_REPOSITORY")
    if (workflow_run.get("repository") or {}).get("full_name") != expected_repository:
        raise PublisherContractError("source workflow repository mismatch")
    if workflow_run.get("name") != expected_workflow:
        raise PublisherContractError("source workflow name mismatch")
    if workflow_run.get("event") != "pull_request":
        raise PublisherContractError("source workflow must be a pull_request run")
    if workflow_run.get("status") != "completed":
        raise PublisherContractError("source workflow is not complete")
    conclusion = workflow_run.get("conclusion")
    if conclusion not in {"success", "failure"}:
        raise PublisherContractError("source workflow conclusion must be success or failure")
    run_id = workflow_run.get("id")
    if isinstance(run_id, bool) or not isinstance(run_id, int) or run_id <= 0:
        raise PublisherContractError("source workflow run ID must be a positive integer")
    head_sha = workflow_run.get("head_sha")
    if not isinstance(head_sha, str) or not SHA_PATTERN.fullmatch(head_sha):
        raise PublisherContractError("source workflow head SHA must be 40 lowercase hex characters")
    pull_requests = workflow_run.get("pull_requests")
    if not isinstance(pull_requests, list) or len(pull_requests) != 1:
        raise PublisherContractError("source workflow must be associated with exactly one PR")
    pull_request_number = pull_requests[0].get("number")
    if (
        isinstance(pull_request_number, bool)
        or not isinstance(pull_request_number, int)
        or pull_request_number <= 0
    ):
        raise PublisherContractError("pull-request number must be a positive integer")
    html_url = workflow_run.get("html_url")
    if not isinstance(html_url, str) or not html_url.startswith(
        f"https://github.com/{expected_repository}/actions/runs/{run_id}"
    ):
        raise PublisherContractError("source workflow URL mismatch")
    return SourceRun(
        repository=expected_repository,
        workflow=expected_workflow,
        run_id=run_id,
        head_sha=head_sha,
        pull_request_number=pull_request_number,
        conclusion=conclusion,
        html_url=html_url,
    )


def select_artifact(payload: dict[str, Any]) -> dict[str, Any]:
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise PublisherContractError("artifact API response is malformed")
    total_count = payload.get("total_count")
    if isinstance(total_count, bool) or not isinstance(total_count, int):
        raise PublisherContractError("artifact API response has an invalid total_count")
    if total_count != len(artifacts):
        raise PublisherContractError("artifact response is incomplete or paginated")
    matches = [item for item in artifacts if item.get("name") == ARTIFACT_NAME]
    if len(matches) != 1:
        raise PublisherContractError("expected exactly one RAGOps evidence artifact")
    artifact = matches[0]
    if artifact.get("expired") is not False:
        raise PublisherContractError("RAGOps evidence artifact is expired")
    size = artifact.get("size_in_bytes")
    if isinstance(size, bool) or not isinstance(size, int) or not 0 < size <= MAX_ARCHIVE_BYTES:
        raise PublisherContractError("RAGOps evidence artifact exceeds the archive size limit")
    archive_url = artifact.get("archive_download_url")
    if not isinstance(archive_url, str) or not archive_url.startswith("https://api.github.com/"):
        raise PublisherContractError("artifact download URL is not a GitHub API URL")
    return artifact


def read_evidence_archive(archive: bytes, source: SourceRun) -> str:
    if not 0 < len(archive) <= MAX_ARCHIVE_BYTES:
        raise PublisherContractError("downloaded artifact exceeds the archive size limit")
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            infos = bundle.infolist()
            names = [info.filename for info in infos]
            allowed_sets = {REQUIRED_FILES, REQUIRED_FILES | OPTIONAL_FILES}
            if len(names) != len(set(names)) or frozenset(names) not in allowed_sets:
                raise PublisherContractError("artifact file allowlist mismatch")
            total_size = 0
            for info in infos:
                mode = info.external_attr >> 16
                if info.is_dir() or stat.S_ISLNK(mode):
                    raise PublisherContractError("artifact contains a non-regular file")
                if info.file_size < 0:
                    raise PublisherContractError("artifact contains an invalid file size")
                total_size += info.file_size
            if total_size > MAX_TOTAL_UNCOMPRESSED_BYTES:
                raise PublisherContractError("artifact exceeds the uncompressed size limit")
            report_bytes = bundle.read("ragops-report.md")
            manifest_bytes = bundle.read("ragops-evidence.json")
    except zipfile.BadZipFile as exc:
        raise PublisherContractError("artifact is not a valid ZIP archive") from exc
    if not report_bytes or len(report_bytes) > MAX_REPORT_BYTES:
        raise PublisherContractError("Markdown evidence exceeds the report size limit")
    if not manifest_bytes or len(manifest_bytes) > MAX_MANIFEST_BYTES:
        raise PublisherContractError("evidence manifest exceeds the manifest size limit")
    try:
        report = report_bytes.decode("utf-8")
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PublisherContractError("artifact evidence must be valid UTF-8 and JSON") from exc
    expected = {
        "schema_version": "ragops-github-evidence-0.1",
        "repository": source.repository,
        "event_name": "pull_request",
        "workflow": source.workflow,
        "run_id": source.run_id,
        "head_sha": source.head_sha,
        "pull_request_number": source.pull_request_number,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise PublisherContractError(f"evidence manifest mismatch for {key}")
    gate_exit_code = manifest.get("gate_exit_code")
    if gate_exit_code not in {0, 2}:
        raise PublisherContractError("evidence manifest gate exit must be 0 or 2")
    expected_conclusion = "success" if gate_exit_code == 0 else "failure"
    if source.conclusion != expected_conclusion:
        raise PublisherContractError("workflow conclusion does not match gate exit")
    return report.rstrip()


def build_comment(report: str, source: SourceRun, *, has_html: bool = True) -> str:
    decision = "PASS" if source.conclusion == "success" else "BLOCK"
    html_link = (
        f" · [HTML report]({source.html_url}#artifacts) (`ragops-report.html`)"
        if has_html
        else ""
    )
    body = (
        f"{MARKER}\n"
        f"## RAGOps release gate: {decision}\n\n"
        f"{report}\n\n"
        f"---\nCanonical evidence: [workflow run]({source.html_url})"
        f"{html_link} · "
        f"head `{source.head_sha[:12]}`\n"
    )
    if len(body.encode("utf-8")) > 60_000:
        raise PublisherContractError("rendered PR comment exceeds the size limit")
    return body


def marker_comment_id(comments: list[dict[str, Any]]) -> int | None:
    matches = []
    for comment in comments:
        user = comment.get("user") or {}
        body = comment.get("body")
        if (
            user.get("type") == "Bot"
            and user.get("login") == "github-actions[bot]"
            and isinstance(body, str)
            and body.startswith(MARKER)
        ):
            comment_id = comment.get("id")
            if isinstance(comment_id, bool) or not isinstance(comment_id, int):
                raise PublisherContractError("marker comment has an invalid ID")
            matches.append(comment_id)
    if len(matches) > 1:
        raise PublisherContractError("multiple RAGOps bot marker comments found")
    return matches[0] if matches else None


class GitHubClient:
    def __init__(self, token: str) -> None:
        if not token:
            raise PublisherContractError("GITHUB_TOKEN is required")
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ragops-pr-comment-publisher",
        }

    def request_json(self, url: str, *, method: str = "GET", body: dict | None = None) -> Any:
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(url, data=data, headers=self.headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            raise PublisherContractError(f"GitHub API request failed: {method} {url}") from exc

    def request_bytes(self, url: str) -> bytes:
        request = urllib.request.Request(url, headers=self.headers)
        opener = urllib.request.build_opener(_NoRedirect())
        try:
            with opener.open(request, timeout=30) as response:
                data = response.read(MAX_ARCHIVE_BYTES + 1)
        except urllib.error.HTTPError as exc:
            if exc.code not in {301, 302, 303, 307, 308}:
                raise PublisherContractError("GitHub artifact download failed") from exc
            location = exc.headers.get("Location", "")
            validate_artifact_redirect_url(location)
            unsigned_request = urllib.request.Request(
                location, headers={"User-Agent": "ragops-pr-comment-publisher"}
            )
            try:
                with urllib.request.urlopen(unsigned_request, timeout=30) as response:
                    data = response.read(MAX_ARCHIVE_BYTES + 1)
            except (urllib.error.HTTPError, urllib.error.URLError) as redirect_exc:
                raise PublisherContractError("GitHub artifact redirect download failed") from redirect_exc
        except urllib.error.URLError as exc:
            raise PublisherContractError("GitHub artifact download failed") from exc
        if len(data) > MAX_ARCHIVE_BYTES:
            raise PublisherContractError("downloaded artifact exceeds the archive size limit")
        return data

    def request_list_pages(self, url: str, *, max_pages: int = 10) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        separator = "&" if "?" in url else "?"
        for page in range(1, max_pages + 1):
            batch = self.request_json(f"{url}{separator}per_page=100&page={page}")
            if not isinstance(batch, list) or any(not isinstance(item, dict) for item in batch):
                raise PublisherContractError("paginated GitHub API response is malformed")
            items.extend(batch)
            if len(batch) < 100:
                return items
        raise PublisherContractError("GitHub API pagination exceeds the safe page limit")


def publish_comment(*, event_path: Path, repository: str, workflow: str, token: str) -> str:
    try:
        payload = json.loads(event_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PublisherContractError("GITHUB_EVENT_PATH is not valid UTF-8 JSON") from exc
    source = validate_source_event(
        payload, expected_repository=repository, expected_workflow=workflow
    )
    client = GitHubClient(token)
    base = f"https://api.github.com/repos/{repository}"
    artifacts = client.request_json(f"{base}/actions/runs/{source.run_id}/artifacts?per_page=100")
    artifact = select_artifact(artifacts)
    if not artifact["archive_download_url"].startswith(f"{base}/actions/artifacts/"):
        raise PublisherContractError("artifact download URL does not belong to the repository")
    archive = client.request_bytes(artifact["archive_download_url"])
    report = read_evidence_archive(archive, source)
    body = build_comment(report, source, has_html=_archive_has_html(archive))
    comments = client.request_list_pages(f"{base}/issues/{source.pull_request_number}/comments")
    comment_id = marker_comment_id(comments)
    if comment_id is None:
        client.request_json(
            f"{base}/issues/{source.pull_request_number}/comments",
            method="POST",
            body={"body": body},
        )
        return "created"
    client.request_json(
        f"{base}/issues/comments/{comment_id}", method="PATCH", body={"body": body}
    )
    return "updated"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def _archive_has_html(archive: bytes) -> bool:
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        return "ragops-report.html" in bundle.namelist()


def validate_artifact_redirect_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    hostname = (parsed.hostname or "").lower()
    allowed_host = (
        hostname == "objects.githubusercontent.com"
        or hostname.endswith(".githubusercontent.com")
        or hostname.endswith(".blob.core.windows.net")
    )
    if parsed.scheme != "https" or not allowed_host or parsed.username or parsed.password:
        raise PublisherContractError("artifact redirect URL is not an approved HTTPS storage host")


def main() -> int:
    event_path = os.getenv("GITHUB_EVENT_PATH", "")
    repository = os.getenv("GITHUB_REPOSITORY", "")
    workflow = os.getenv("RAGOPS_SOURCE_WORKFLOW", "")
    if not event_path or not repository or not workflow:
        raise SystemExit("GITHUB_EVENT_PATH, GITHUB_REPOSITORY, and RAGOPS_SOURCE_WORKFLOW are required")
    try:
        outcome = publish_comment(
            event_path=Path(event_path),
            repository=repository,
            workflow=workflow,
            token=os.getenv("GITHUB_TOKEN", ""),
        )
    except PublisherContractError as exc:
        raise SystemExit(f"publisher contract error: {exc}") from exc
    print(json.dumps({"comment": outcome}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
