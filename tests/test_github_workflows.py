from pathlib import Path

WORKFLOW_ROOT = Path(".github/workflows")


def test_repository_has_consumer_ci_and_separate_release_publisher() -> None:
    assert sorted(path.name for path in WORKFLOW_ROOT.iterdir()) == [
        "ci.yml",
        "codeql.yml",
        "publish-pypi.yml",
    ]
    workflow = (WORKFLOW_ROOT / "publish-pypi.yml").read_text(encoding="utf-8")
    assert "id-token: write" in workflow
    assert "environment: pypi" in workflow
    assert "pull_request" not in workflow
    assert "pypa/gh-action-pypi-publish@v1.14.2" in workflow
    ci = (WORKFLOW_ROOT / "ci.yml").read_text(encoding="utf-8")
    assert "pull_request:" in ci
    assert 'python-version: ${{ matrix.python-version }}' in ci
    assert '["3.11", "3.12", "3.13"]' in ci
    assert "ruff check ." in ci
    assert "pytest -q" in ci
    assert "ragops demo" in ci
    assert "evidence verify" in ci
    assert "id-token: write" not in ci


def test_windows_no_clone_demo_uses_the_published_package() -> None:
    ci = (WORKFLOW_ROOT / "ci.yml").read_text(encoding="utf-8")
    windows_job = ci.split("  windows-no-clone:", 1)[1]

    assert "runs-on: windows-latest" in windows_job
    assert "actions/checkout@" not in windows_job
    assert "enable-cache: false" in windows_job
    assert "ignore-empty-workdir: true" in windows_job
    assert 'uvx --from "ragops==2.0.2" ragops demo' in windows_job
    assert '$summary.candidate_decision -ne "BLOCK"' in windows_job
    assert "demo-output/release-report.html" in windows_job
    assert "ragops evidence verify --bundle demo-output/evidence" in windows_job


def test_codeql_is_least_privilege_and_immutably_pinned() -> None:
    workflow = (WORKFLOW_ROOT / "codeql.yml").read_text(encoding="utf-8")

    assert "contents: read" in workflow
    assert "security-events: write" in workflow
    assert "pull_request_target" not in workflow
    assert "languages: python" in workflow
    assert "build-mode: none" in workflow
    assert workflow.count(
        "github/codeql-action/"
        "init@db488ddef3bf6cb639b32c2e9a7c0a7ea8271d28"
    ) == 1
    assert workflow.count(
        "github/codeql-action/"
        "analyze@db488ddef3bf6cb639b32c2e9a7c0a7ea8271d28"
    ) == 1


def test_current_operations_are_linked() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    for guide in (
        "docs/ARCHITECTURE.md",
        "docs/OPERATIONS.md",
        "docs/releases/v2.0.2.md",
    ):
        assert Path(guide).is_file()
        assert guide in readme
