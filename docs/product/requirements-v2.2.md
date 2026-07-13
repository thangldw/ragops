# RAGOps v2.2 requirement: quota-independent release fallback

## Contract

When GitHub Actions is unavailable or out of quota, the owner can run the same
quality gates locally, build artifacts once, and publish those exact artifacts
without enabling Actions.

Acceptance requires Ruff, the complete offline test suite, PASS and BLOCK
benchmark checks, package build, reproducible CycloneDX SBOM, SHA-256 manifest,
and machine-readable local evidence. GitHub publication uses `gh` directly.
PyPI publication is opt-in and fails closed unless a project-scoped API token is
provided through `PYPI_API_TOKEN`.

## Compatibility

This is an additive operational path. It does not change public schemas, metric
meaning, gate thresholds, CLI contracts, or the open-core boundary.

## Non-goals

- Bypassing PyPI authentication or claiming OIDC provenance for a local build.
- Replacing the normal Trusted Publishing path after Actions capacity returns.
- Running security tests in this phase.
