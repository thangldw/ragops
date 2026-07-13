# Product roadmap

## Project status

The program is complete and active development is paused as of 2026-07-13.
The repository remains public at stable release `2.4.0` for adoption and
feedback. This capability map is retained for reference; resuming development
requires a concrete user need, owner review, and a new scoped requirement.

This file is a released-capability map, not an active implementation queue.
There are no open repository milestones after v2.4; new work starts only after
owner review of a concrete user need.

## 1.0 — stable local core (released)

Portable contracts, deterministic gates, baseline comparison, plugins, local
history, CLI/API/workbench, CI, and container baseline.

## 1.1 — credible benchmark (released)

- Expand the Japanese troubleshooting scenario and publish its taxonomy.
- Add claim-level citation precision and completeness.
- Add attack-pack contracts for prompt injection and permission leakage.
- Improve failure drill-down in HTML reports.

## 1.2 — real application adapters (released)

- Reference RAG/agent application producing portable traces.
- OpenTelemetry and generic HTTP/provider adapters.
- Model, prompt, retriever, dataset, and build metadata.
- Statistical summaries and evaluator calibration guidance.

## 1.3 — team workflow (released for local workspace)

- Browser run explorer and metric trends.
- Review status and accepted baseline workflow.
- Scheduled benchmark/reference suite.

PR comment integration and notifications remain hosted/integration work.

## 1.4 — complete reference program (released)

- Japanese Graph+ACL reference deployment with portable trace 0.4 output.
- Thirty-case synthetic benchmark, attack metadata, and separated evidence.
- Local team review/trend workflow and control-plane alpha boundary.
- Optional HTTP and OpenAI Responses API adapters outside the core.

## 1.5 — adoption-first developer experience (released)

- Credential-free `ragops demo` command and reviewable report bundle.
- Problem/solution/demo/evidence/limitations product showcase.
- MIT licensing, contributor onboarding, and repository discovery assets.
- PyPI distribution, PR-native GitHub Action, starter issues, and public
  discovery assets.

## 1.6 — pull-request adoption path (released)

- Reusable read-only GitHub PR gate with evidence summary and artifact.
- Print-ready standalone HTML comparison report.
- Framework-neutral first-trace tutorial.
- Dependency-free OpenTelemetry span-to-trace example.
- Manual PyPI Trusted Publishing workflow with release 1.6.0 published through
  GitHub OIDC.

## 1.7 — broader adoption proof (released)

- Second credential-free support-triage demo scenario.
- Third credential-free proposal-review demo scenario.
- Deterministic, configurable Unicode code-point answer-length evaluator.
- GitHub discovery metadata, Discussions, and real starter issues.
- GitLab CI release-gate recipe and reviewed least-privilege PR-comment design.

## 1.8 — review visibility and measured adoption (released)

- Isolated, write-enabled PR comment publisher with bounded artifact parsing,
  exact metadata verification, pinned actions, and idempotent updates.
- Portable design-partner manifest, JSONL observations, optional economics,
  deterministic KPI/ROI report, and explicit evidence limits.
- Synthetic rehearsal, consent/data-minimization runbook, and public design-
  partner outreach pack.

## 2.0 — trustworthy extensible release gates (released)

- First-class opt-in custom metric and finding-severity gates.
- Unified evaluator semantics across absolute evaluation and comparison.
- Strict numeric validation and official response-list schema.
- Fail-closed API authentication, bounded input, and explicit local dev mode.
- Synthetic benchmark positioning and evidence-safe workbench error states.

## 2.1 — portable external evaluator evidence (released)

- Versioned per-case external metric envelope for Ragas, DeepEval, Langfuse,
  and internal judges.
- Shared absolute gate semantics and baseline/candidate deltas without provider
  dependencies in the core.
- Copyable downstream PR-comment publisher recipe with explicit trust boundary.

## 2.2 — quota-independent release fallback (released)

- Local quality gates, build-once packages, SBOM, checksums, and evidence.
- Direct GitHub CLI publication and fail-closed project-token PyPI promotion.

## 2.3 — release integrity and discoverability (released)

- Installed CLI version diagnostics.
- Clean-wheel smoke testing before tagging.
- Dependency-free cross-platform checksum verification.

## 2.4 — adoption experience refresh (released)

- Decision-first README and five-minute install-to-evidence onboarding.
- Interactive developer-proof showcase with implementation-derived screenshots.
- Unified demo, portfolio, presentation, CV/LinkedIn, and launch copy.
- Evidence-safe product claims and explicit measurement limits.

## Deferred hypothesis — hosted control plane

- Workspace isolation, SSO/RBAC, audit retention, managed ingestion, and
  enterprise deployment options.

The repository already contains a bounded local alpha with workspace-isolated
stores, generated/digested keys, rotation, and audit events. A hosted product is
not active roadmap work; it would require separate owner approval plus cloud,
identity, legal, security, operations, and design-partner evidence.
