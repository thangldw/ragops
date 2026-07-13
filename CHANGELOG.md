# Changelog

All notable changes follow Keep a Changelog. This project uses Semantic Versioning.

## [Unreleased]

### Added

- Deterministic publisher fixtures for single-association fork PRs, expired and
  paginated artifacts, bounded comment enumeration, and GitHub API rate limits.
- An explicit adapter retention decision: repositories own artifact/comment
  lifecycle, while the publisher remains bounded and fail closed.

### Changed

- Repositioned public discovery copy around regression tests and explainable
  release gates for teams that already have a RAG or AI agent.
- Removed obsolete active-planning documents after program completion and
  aligned current roadmap, launch, observability, and presentation copy with
  the released v2.4 state. Historical ADRs, requirements, acceptance records,
  and release notes remain unchanged.
- Rebuilt the GitHub Pages showcase around a decision-first regression proof,
  shortened the mobile narrative, replaced mutable test-count marketing with
  stable product signals, and refreshed public screenshots and social preview.

## [2.4.0] - 2026-07-13

### Changed

- Reframed the public adoption experience around the five-minute path from
  installation to an explainable PASS/BLOCK release decision.
- Rebuilt the showcase hero as a responsive, interactive developer proof with
  copyable commands and recorded portable evidence.
- Rewrote getting-started, demo, portfolio, presentation, video, CV/LinkedIn,
  and GitHub launch materials with one evidence-safe product narrative.
- Replaced the primary README visual with a screenshot captured from the real
  implementation and refreshed design-QA evidence.

## [2.3.0] - 2026-07-13

### Added

- `ragops --version` for installed-package and support diagnostics.
- Clean-wheel installation smoke testing in the local release verification lane.

### Changed

- Local artifact checksum verification is dependency-free and portable across
  supported operating systems.
- Public documentation, roadmap, release evidence, and integration examples now
  identify the current stable release consistently.

## [2.2.0] - 2026-07-13

### Added

- Quota-independent local release fallback with full offline validation,
  build-once artifacts, reproducible SBOM, checksums, GitHub CLI publication,
  and fail-closed optional PyPI token promotion.

## [2.1.0] - 2026-07-13

### Added

- Portable external metric envelope and dependency-free evaluator bridge for
  per-case scores exported by Ragas, DeepEval, Langfuse, or internal judges.
- CLI support for external metrics in both absolute evaluation and baseline
  comparison, with exact coverage/provider/metric compatibility checks.
- Copyable downstream GitHub PR-comment publisher recipe with a commit-pinned
  trusted publisher checkout and explicit workflow-name allowlist.

## [2.0.0] - 2026-07-13

### Added

- Optional evaluation-policy TOML contract for minimum/maximum custom metric
  gates and configurable finding-severity gates.
- Unified evaluator selection and absolute gate semantics across `evaluate` and
  `compare`, including custom metric deltas.
- Official JSON Schema for recorded response lists and documented evaluator
  gate examples.
- Build provenance attestation, reproducible CycloneDX SBOM, and SHA-256 release
  manifest generated beside each GitHub Release artifact.

### Changed

- Scenario, response, trace, evaluator, and policy numeric values now fail
  closed on non-finite, negative, boolean, or out-of-range values.
- Protected API endpoints require a configured key by default; explicit local
  bypass uses `RAGOPS_INSECURE_DEV_MODE=true`. Compose requires a key, binds to
  localhost, and configures request/case limits.
- The Japanese troubleshooting suite is labeled as a synthetic release-gate
  fixture rather than evidence of Japanese semantic quality.
- Release automation builds wheel/source once and promotes those exact verified
  GitHub Release artifacts to PyPI; CI covers Python 3.11, 3.12, and 3.13 and
  GitHub Actions are commit-pinned.

## [1.8.0] - 2026-07-13

### Added

- Isolated, least-privilege GitHub `workflow_run` publisher that validates a
  bounded evidence artifact and creates or updates one idempotent PR comment.
- Portable design-partner pilot manifest, observation, economics, and report
  contracts with deterministic adoption, task-outcome, safety, time-saved, and
  optional ROI estimates.
- Synthetic pilot rehearsal fixtures, generated report, measurement plan, and
  real-pilot runbook with explicit consent and evidence limits.

## [1.7.0] - 2026-07-13

### Added

- Second credential-free `support-triage` demo scenario with an intentionally
  blocked unsafe candidate.
- Configurable `answer_length_budget` evaluator using deterministic Unicode
  code-point counts, CLI support, diagnostics, and documented limitations.
- Credential-free `proposal-review` demo with an intentionally unsupported,
  uncited requirement candidate.
- Copyable GitLab merge-request release-gate recipe with always-on evidence
  artifacts.
- Least-privilege PR-comment publishing ADR and trust-boundary design; the
  current GitHub workflow remains read-only.

### Changed

- PyPI distribution is active through OIDC Trusted Publishing and requires no
  stored API token.

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
