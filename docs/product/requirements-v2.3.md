# Requirements v2.3 — release integrity and discoverability

## User story

As a maintainer or adopter, I can identify the installed RAGOps version and
verify that a locally built wheel installs cleanly before publication, even when
GitHub Actions is unavailable.

## Acceptance criteria

- `ragops --version` prints the package version and exits zero.
- Local release verification installs the built wheel into a fresh virtualenv.
- Artifact checksums are verified in dependency-free Python on every supported
  operating system and reject missing, traversing, or tampered targets.
- Current-state documentation and integration examples reference one stable
  release; historical release records remain unchanged.
- Ruff, full tests, deterministic PASS/BLOCK fixtures, package build, clean
  install, GitHub Release, and exact PyPI promotion pass locally.

## Compatibility and non-goals

The CLI flag and release checks are additive. No schema, metric, gate meaning,
API contract, or open-core boundary changes. Hosted infrastructure, real-user
adoption evidence, and security testing are outside this release.
