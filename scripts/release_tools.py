#!/usr/bin/env python3
"""Release helpers: one-command version bump and pre-release checks.

    python scripts/release_tools.py bump 2.4.0     # edits every version-bearing file
    python scripts/release_tools.py check 2.4.0    # refuses burned/used/older versions
    python scripts/release_tools.py check 2.4.0 --offline
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = re.compile(r"\d+\.\d+\.\d+")

# (file, regex with one group around the old version, replacement template using {new})
PLAIN_FILES = (
    "src/ragops/__init__.py",
    ".kimi-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    "action.yml",
    "docs/examples/gitlab-ci-ragops.yml",
    "docs/examples/github-actions-ragops.yml",
    "docs/submission/DIRECTORY_SUBMISSION.md",
)


class ReleaseError(Exception):
    pass


def current_version(root: Path = ROOT) -> str:
    return tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


def parse(version: str) -> tuple[int, int, int]:
    if not VERSION.fullmatch(version):
        raise ReleaseError(f"version must be MAJOR.MINOR.PATCH, got {version!r}")
    major, minor, patch = (int(part) for part in version.split("."))
    return major, minor, patch


def burned(root: Path = ROOT) -> set[str]:
    path = root / "scripts" / "burned_versions.txt"
    if not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }


def bump(new: str, root: Path = ROOT) -> list[str]:
    old = current_version(root)
    if parse(new) <= parse(old):
        raise ReleaseError(f"new version {new} must be greater than current {old}")
    if new in burned(root):
        raise ReleaseError(f"{new} is listed in burned_versions.txt")
    changed: list[str] = []

    def rewrite(relative: str, transform) -> None:
        path = root / relative
        text = path.read_text(encoding="utf-8")
        updated = transform(text)
        if updated == text:
            raise ReleaseError(f"{relative}: found nothing to update for {old}")
        path.write_text(updated, encoding="utf-8")
        changed.append(relative)

    rewrite("pyproject.toml", lambda t: t.replace(f'version = "{old}"', f'version = "{new}"', 1))
    for relative in PLAIN_FILES:
        rewrite(relative, lambda t: t.replace(old, new))
    rewrite("README.md", lambda t: t.replace(f"v{old}", f"v{new}"))
    notes = root / "docs" / "releases" / f"v{new}.md"
    if not notes.exists():
        notes.parent.mkdir(parents=True, exist_ok=True)
        notes.write_text(
            f"# RAGOps v{new}\n\nSummarize the user-visible changes here before releasing.\n",
            encoding="utf-8",
        )
        changed.append(f"docs/releases/v{new}.md")
    changelog = root / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8")
    if "## Unreleased" in text and f"## [{new}]" not in text:
        date = datetime.now(UTC).date().isoformat()
        changelog.write_text(text.replace("## Unreleased", f"## [{new}] - {date}", 1), encoding="utf-8")
        changed.append("CHANGELOG.md")
    return changed


def _fetch_json(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=15) as response:  # noqa: S310 (fixed https URLs)
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise ReleaseError(f"cannot query {url}: HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"cannot query {url}: {exc}") from exc


def check(new: str, root: Path = ROOT, *, offline: bool = False) -> list[str]:
    problems: list[str] = []
    parse(new)
    if current_version(root) != new:
        problems.append(f"pyproject.toml version is {current_version(root)}, expected {new}")
    if new in burned(root):
        problems.append(f"{new} was used on PyPI and deleted; PyPI will refuse the filename")
    if f"## [{new}]" not in (root / "CHANGELOG.md").read_text(encoding="utf-8"):
        problems.append(f"CHANGELOG.md has no [{new}] section")
    if not (root / "docs" / "releases" / f"v{new}.md").is_file():
        problems.append(f"docs/releases/v{new}.md is missing")
    if not offline:
        data = _fetch_json("https://pypi.org/pypi/ragops/json")
        if data is not None:
            existing = set(data["releases"])
            if new in existing:
                problems.append(f"{new} already exists on PyPI")
            latest = max((parse(v) for v in existing if VERSION.fullmatch(v)), default=(0, 0, 0))
            if parse(new) <= latest:
                problems.append(f"{new} is not newer than the latest PyPI release {'.'.join(map(str, latest))}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("bump").add_argument("version")
    checker = sub.add_parser("check")
    checker.add_argument("version")
    checker.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "bump":
            for relative in bump(args.version):
                print(f"updated {relative}")
            print("Now edit docs/releases/v%s.md and the CHANGELOG, then run `check`." % args.version)
            return 0
        problems = check(args.version, offline=args.offline)
    except ReleaseError as exc:
        print(f"release error: {exc}", file=sys.stderr)
        return 1
    if problems:
        for problem in problems:
            print(f"BLOCKED: {problem}", file=sys.stderr)
        return 1
    print(f"{args.version}: ready to release")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
