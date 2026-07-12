# Changelog

All notable changes follow Keep a Changelog. This project uses Semantic Versioning.

## [Unreleased]

## [1.6.0] - 2026-07-13

### Added

- Reusable, read-only GitHub pull-request release gate with Step Summary and
  evidence artifact output.
- Credential-free portable trace tutorial and a manual, OIDC-based PyPI Trusted
  Publishing workflow with tag/version verification.
- Dependency-free OpenTelemetry span-to-trace example with synthetic fixtures,
  strict contract errors, and trace 0.4 compatibility coverage.

### Changed

- Standalone HTML comparison reports now include print-ready A4 styles.
- Release-check virtual environments are excluded from source distributions.

## [1.5.0] - 2026-07-12

### Added

- Credential-free `ragops demo` command that writes portable fixtures plus
  Markdown and HTML release-decision evidence.
- Adoption-first showcase sections for the problem, solution flow, reference
  demo, separated evidence sets, architecture boundary, limitations, and
  contributor paths.
- Contributor code of conduct, support guidance, and structured bug reports.
- Dependency-free optional OpenAI Responses API adapter with explicit model,
  output/usage mapping, injected-transport tests, and provider guidance.
- A focused 16:9 product-showcase image for the GitHub README.
- Design-partner outreach and pilot measurement templates, plus CV/LinkedIn
  copy based on public evidence.

### Changed

- Repository HEAD and future releases now use the MIT License; previously
  published Apache-2.0 releases retain their original license.
- Reworked the README around the product value, reproducible evidence, quick
  start, architecture boundaries, and honest production limitations.
- Updated the product showcase to reflect the current 50+ test validation suite.
- Expanded the GitHub README with two architecture/evidence infographics and
  current desktop, limitations, and mobile product screens.

### Security

- Made `ragops demo` fail closed for existing output directories and reject
  symlinked destinations or files; intentional replacement now requires
  `--force` and uses an atomic temporary-file swap.

### Fixed

- Repaired the malformed trace 0.4 JSON Schema object boundary and added a
  regression gate that parses every published schema.

## [1.4.0] - 2026-07-12

### Added

- Product personas, jobs to be done, success metrics, competitive positioning,
  commercialization boundary, and staged roadmap.
- Milestones, work breakdown, risk register, release plan, and decision log.
- Context/component diagrams, data model, threat model, and architecture decisions
  for reference applications and the open-core boundary.
- Engineering, evaluation, red-team, demo, portfolio, and AI-collaboration guidance.
- Repository skills for feature implementation, release validation, and presentations.
- Backwards-compatible scenario 0.2 metadata and citation-precision release gates.
- Portable red-team attack-pack contract with a Japanese enterprise sample pack.
- Per-case failure drill-down in standalone HTML comparison reports.
- A 30-case Japanese enterprise troubleshooting benchmark with nine case
  families, attack metadata, a passing baseline, coverage tests, and CI gates.
- Response-fixture overlays, explicit regressed/adversarial benchmark candidates,
  expected-failure CI checks, and a reproducible benchmark report.
- Optional claim-support and citation-correctness evaluators with aggregate
  plugin metrics, calibration tests, CLI selection, and M1 acceptance evidence.
- A credential-free Japanese GraphRAG-style reference agent with ACL filtering,
  workflow decisions, trace 0.4 metadata, JSONL CLI evaluation/comparison,
  generic HTTP adapter, recorded regression experiment, and M2 acceptance.
- A responsive FDE case-study site, GitHub Pages workflow, reproducible metrics,
  video script, personal-portfolio handoff, and M3 acceptance evidence.
- Local team review metadata and metric trends across SQLite, CLI, API, and the
  browser workbench, plus nightly benchmark/reference-deployment gates and M4
  acceptance evidence.
- A local commercial control-plane alpha with workspace-isolated stores,
  generated/digested API keys, rotation, audit events, CLI management, API
  workspace selection, persisted evaluation, and explicit production limits.

## [1.0.0] - 2026-07-12

### Added

- Portable scenario, trace, evaluation, and comparison contracts.
- Deterministic citation, groundedness, budget, and red-team gates.
- Baseline-aware regression comparison with configurable tolerances.
- Custom evaluator protocol and registry.
- JSONL trace ingestion and retrieval recall evaluator.
- JSON, Markdown, and standalone HTML reports.
- SQLite experiment history.
- CLI, FastAPI endpoints, and local evaluation workbench.
- Docker runtime, CI matrix, release workflow, and Japanese enterprise scenario.

### Security

- Optional API-key authentication using constant-time comparison.
- Non-root, read-only container defaults with no-new-privileges.
- Offline core with no required model-provider connection.
