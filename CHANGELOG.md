# Changelog

RAGOps follows [Semantic Versioning](https://semver.org/). This file is the
single release-history source in the current tree; detailed historical context
remains available in Git.

## [Unreleased]

## [2.5.0] - 2026-07-15

### Added

- Added an experimental, opt-in `compare-runs` command with versioned replay
  bundles, provenance checks, deterministic paired hierarchical bootstrap
  bounds, and uncertainty-aware absolute and regression gates.
- Added JSON schemas for replay bundles and statistical comparison reports plus
  credential-free PASS/BLOCK fixtures.
- Added bounded, shell-free repeated-run collection with atomic checkpoints,
  resume support, and sequential early stopping.
- Added predeclared group-sequential gates, evaluator-drift equivalence checks,
  and provenance diagnosis for model, evaluator, dataset, and infrastructure
  changes.
- Added content-addressed accepted-baseline manifests and optional detached SSH
  signing and offline verification.
- Added dependency-free recorded-score bridges for Ragas, DeepEval, and
  OpenTelemetry GenAI evaluation events.
- Added authenticated bounded statistical API endpoints and a reusable read-only
  GitHub statistical gate with safe PR evidence publication.

### Changed

- Consolidated product, architecture, engineering, evaluation, pilot, demo,
  and project guidance into one current document per topic.
- Rebuilt documentation diagrams and infographics with a consistent
  Miro-inspired board style using only local system fonts.
- Simplified GitHub Pages deployment to publish `site/` from `main`.

### Removed

- Superseded requirement snapshots, acceptance records, release-note copies,
  design-audit captures, and duplicate guides from the current tree.

## [2.4.0] - 2026-07-13

### Changed

- Reframed the public experience around a five-minute path from installation
  to an explainable PASS/BLOCK decision.
- Rebuilt the Pages showcase and current product visuals around portable,
  reproducible evidence and explicit limitations.

## [2.3.0] - 2026-07-13

### Added

- `ragops --version`, clean-wheel smoke testing, portable checksum validation,
  and consistent release-integrity evidence.

## [2.2.0] - 2026-07-13

### Added

- A quota-independent local release lane with offline validation, build-once
  artifacts, reproducible SBOM, checksums, and explicit promotion steps.

## [2.1.0] - 2026-07-13

### Added

- Portable external metric envelopes and evaluator bridges.
- A trusted, commit-pinned GitHub pull-request comment publisher recipe.

## [2.0.0] - 2026-07-13

### Added

- Evaluation-policy TOML, first-class evaluator gates, custom metric deltas,
  strict numeric validation, provenance attestations, and reproducible SBOMs.

### Security

- Protected API endpoints fail closed unless authentication or explicit local
  development mode is configured.

## [1.8.0] - 2026-07-13

### Added

- Isolated PR-comment publishing and portable design-partner pilot evidence.

## [1.7.0] - 2026-07-13

### Added

- Support-triage and proposal-review demos, answer-length gates, and a GitLab
  merge-request recipe.

## [1.6.0] - 2026-07-13

### Added

- A reusable read-only GitHub PR gate, OpenTelemetry trace adapter, and
  OIDC-based PyPI publishing path.

## [1.5.0] - 2026-07-12

### Added

- `ragops demo`, adoption-first showcase assets, an optional OpenAI adapter,
  contributor guidance, and design-partner templates.

### Security

- Demo output replacement became symlink-safe and atomic.

## [1.4.0] - 2026-07-12

### Added

- Product and architecture foundations, benchmark fixtures, evaluator plugins,
  the Japanese troubleshooting reference agent, team review workflow, and the
  local control-plane alpha.

## [1.0.0] - 2026-07-12

### Added

- Portable scenarios, traces, deterministic evaluation and comparison gates,
  reports, SQLite history, CLI, API, workbench, Docker, and CI.

### Security

- Optional constant-time API-key authentication, hardened container defaults,
  and a provider-independent offline core.
