# Testing and release

## Development checks

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,api]'
ruff check .
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```

Tests cover contracts, evaluator boundaries, engine integration, adapters,
reports, supported schemas, passing baselines, and blocked regressions. Core
tests remain offline and credential-free.

## Release checklist

1. Link the current requirement and architecture decisions.
2. Confirm version consistency across package, API, reports, changelog, tag, and
   release metadata.
3. Run lint, full tests, schema checks, PASS/BLOCK samples, API health/evaluate,
   package build, and clean-wheel install.
4. Review dependency, security, generated-file, secret, and Git status changes.
5. Build wheel and source archive once; generate checksums, SBOM, and acceptance
   evidence from those exact artifacts.
6. Obtain owner acceptance before tag, GitHub Release, PyPI, or other public
   publication.

## GitHub release path

The preferred workflow uses OIDC provenance and promotes already-verified
artifacts. Release notes are generated from Git history and `CHANGELOG.md`; HEAD
does not maintain duplicate per-version Markdown files.

## Local fallback

When GitHub Actions is unavailable:

```bash
python -m pip install -e '.[dev]' build cyclonedx-bom==7.3.0 twine
python scripts/local_release.py verify --tag vX.Y.Z
python scripts/local_release.py publish-github --tag vX.Y.Z --yes
```

Emergency PyPI publication requires a short-lived project-scoped token and must
promote artifacts downloaded back from the GitHub Release without rebuilding.
Local-token evidence records `trusted_publishing: false`.

## Rollback

Published package files and public contracts are immutable. Yank when
appropriate, restore the last working behavior, add a permanent regression
test, and publish a corrective version. Never silently replace an artifact or
reinterpret a released metric.
