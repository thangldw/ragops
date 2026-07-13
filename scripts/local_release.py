#!/usr/bin/env python3
"""Quota-independent release lane for RAGOps.

Build and validate locally, then publish the exact artifacts to GitHub and,
only with an explicitly supplied project-scoped token, PyPI.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def run(
    *args: str,
    env: dict[str, str] | None = None,
    cwd: Path = ROOT,
) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=cwd, env=env, check=True)


def version() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def assert_tag(tag: str) -> str:
    expected = f"v{version()}"
    if tag != expected:
        raise SystemExit(f"tag {tag!r} does not match package version {expected!r}")
    if not (ROOT / "docs" / "releases" / f"{tag}.md").is_file():
        raise SystemExit(f"missing release notes: docs/releases/{tag}.md")
    return expected


def artifacts() -> list[Path]:
    result = sorted(DIST.glob("ragops-*.whl")) + sorted(DIST.glob("ragops-*.tar.gz"))
    if len(result) != 2:
        raise SystemExit("expected exactly one wheel and one source distribution in dist/")
    return result


def checksums(paths: list[Path]) -> Path:
    manifest = DIST / "SHA256SUMS"
    lines = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}" for path in paths]
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def verify(tag: str) -> None:
    assert_tag(tag)
    run("ruff", "check", ".")
    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    run(sys.executable, "-m", "pytest", "-q", env=env)
    run("ragops", "evaluate", "--scenario", "scenarios/japanese_troubleshooting/scenario.json",
        "--responses", "scenarios/japanese_troubleshooting/sample_responses.json")
    blocked = subprocess.run(
        ["ragops", "compare", "--scenario", "scenarios/japanese_troubleshooting/benchmark-v0.2.json",
         "--baseline", "scenarios/japanese_troubleshooting/benchmark-baseline.json", "--candidate",
         "scenarios/japanese_troubleshooting/benchmark-regressed.json"], cwd=ROOT
    )
    if blocked.returncode != 2:
        raise SystemExit(f"expected regression gate exit 2, got {blocked.returncode}")
    shutil.rmtree(DIST, ignore_errors=True)
    run(sys.executable, "-m", "build")
    built = artifacts()
    sbom = DIST / f"ragops-{version()}.cdx.json"
    if shutil.which("cyclonedx-py"):
        run("cyclonedx-py", "environment", sys.executable, "--output-reproducible",
            "--output-file", str(sbom))
    else:
        raise SystemExit("cyclonedx-py is required: python -m pip install cyclonedx-bom==7.3.0")
    manifest = checksums([*built, sbom])
    evidence = {
        "schema": "ragops-local-release-evidence-0.1",
        "tag": tag,
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "created_at": datetime.now(UTC).isoformat(),
        "validation": "pass",
        "trusted_publishing": False,
        "artifacts": [path.name for path in [*built, sbom, manifest]],
    }
    (DIST / "LOCAL_RELEASE_EVIDENCE.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
    )


def github(tag: str, yes: bool) -> None:
    assert_tag(tag)
    if not yes:
        raise SystemExit("publishing requires --yes")
    paths = [*artifacts(), DIST / f"ragops-{version()}.cdx.json", DIST / "SHA256SUMS",
             DIST / "LOCAL_RELEASE_EVIDENCE.json"]
    if any(not path.is_file() for path in paths):
        raise SystemExit("run verify first; release artifacts are incomplete")
    run("git", "diff", "--quiet")
    run("git", "diff", "--cached", "--quiet")
    run("git", "tag", "-a", tag, "-m", f"RAGOps {tag}")
    run("git", "push", "origin", tag)
    run("gh", "release", "create", tag, *(str(path) for path in paths), "--verify-tag",
        "--title", f"RAGOps {tag}", "--notes-file", f"docs/releases/{tag}.md")


def pypi(tag: str, yes: bool) -> None:
    assert_tag(tag)
    token = os.environ.get("PYPI_API_TOKEN")
    if not yes or not token:
        raise SystemExit("PyPI publish requires --yes and PYPI_API_TOKEN (project-scoped)")
    release_dir = ROOT / ".local-release" / tag
    shutil.rmtree(release_dir, ignore_errors=True)
    release_dir.mkdir(parents=True)
    run("gh", "release", "download", tag, "--dir", str(release_dir))
    run("shasum", "-a", "256", "-c", "SHA256SUMS", cwd=release_dir)
    distributions = sorted(release_dir.glob("ragops-*.whl")) + sorted(release_dir.glob("ragops-*.tar.gz"))
    if len(distributions) != 2:
        raise SystemExit("GitHub Release must contain exactly one wheel and one source distribution")
    env = os.environ.copy()
    env.update({"TWINE_USERNAME": "__token__", "TWINE_PASSWORD": token})
    run(sys.executable, "-m", "twine", "upload", *(str(path) for path in distributions), env=env)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("verify", "publish-github", "publish-pypi"):
        command = sub.add_parser(name)
        command.add_argument("--tag", required=True)
        if name != "verify":
            command.add_argument("--yes", action="store_true")
    args = parser.parse_args()
    if args.command == "verify":
        verify(args.tag)
    elif args.command == "publish-github":
        github(args.tag, args.yes)
    else:
        pypi(args.tag, args.yes)


if __name__ == "__main__":
    main()
