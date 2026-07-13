# ADR 0019: Local release fallback

Status: Accepted for owner review

## Decision

Provide `scripts/local_release.py` with three explicit phases: `verify`,
`publish-github`, and `publish-pypi`. Verification produces immutable package
artifacts, an SBOM, checksums, and local evidence. GitHub publication requires
`--yes`; PyPI additionally requires a project-scoped token supplied only via an
environment variable and promotes the artifacts downloaded back from GitHub.

Workflows may be disabled through the GitHub UI or `gh workflow disable` while
quota is exhausted. They remain versioned so the owner can restore the preferred
OIDC/provenance path later.

## Consequences

The fallback avoids Actions minutes and keeps release gates observable. Local
PyPI uploads do not receive GitHub Trusted Publisher identity or GitHub build
provenance, so `LOCAL_RELEASE_EVIDENCE.json` records `trusted_publishing: false`.
The owner must protect and rotate the temporary project token.
