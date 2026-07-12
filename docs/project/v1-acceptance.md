# v1.0 acceptance record

## Product loop

- [x] Versioned scenario and portable trace input.
- [x] Absolute quality, budget, and policy release gates.
- [x] Baseline-aware regression gates.
- [x] Extensible evaluator boundary.
- [x] Machine-readable and human-readable reports.
- [x] Local experiment history.
- [x] CLI, HTTP API, and browser workbench.

## Operational readiness

- [x] Dependency-free evaluation core.
- [x] Optional API and development dependency groups.
- [x] Non-root container with read-only compose defaults.
- [x] Optional constant-time API-key check.
- [x] CI on supported Python versions.
- [x] Semantic version and changelog.
- [x] Contribution and security guidance.

## Limitations accepted for v1.0

The first stable release intentionally excludes hosted multi-tenancy,
provider-specific tracing, LLM-as-judge, statistical online evaluation, and
production identity management. These are post-v1 product layers and do not
weaken the local release-gate contract.

