# ADR 0016: First-class evaluator and finding gates

- Status: Accepted for implementation
- Date: 2026-07-13
- Owner authorization: staged implementation and release requested by Thang on
  2026-07-13

## Context

RAGOps aggregates plugin metrics and findings, but only built-in thresholds and
critical findings currently affect PASS/BLOCK. `compare` cannot select
evaluators, so candidate evidence can differ between evaluation paths. Silent
diagnostics undermine the product promise of extensible release governance.

## Decision

Add a separate, optional evaluation-policy TOML contract. Metric gates use the
canonical aggregate metric key emitted in reports and declare exactly one of
`minimum` or `maximum`. Finding gates use the ordered severities `low`,
`medium`, `high`, and `critical` with a configurable failure floor.

The default policy preserves current behavior: no custom metric thresholds and
only critical findings block. Built-in scenario thresholds remain authoritative
and unchanged. Evaluator metric names and meanings are not rewritten; a primary
`score` may receive an additive evaluator-name alias for concise policy use only
when both keys remain present and equal.

`evaluate` and `compare` accept the same evaluator tuple and evaluation policy.
Comparison evaluates baseline and candidate with those same objects and reports
deltas for all shared aggregate numeric metrics. Regression tolerances remain a
separate policy concern.

Policy references fail closed when a named metric is absent. Evaluator output
must be finite. Gate failures use stable names derived from the metric and
direction so reports remain deterministic.

## Compatibility impact

The feature is opt-in and additive. With no evaluation policy and no evaluators,
reports, metrics, gates, and exit codes remain unchanged. Existing plugin metric
keys remain available. Invalid numeric data that was never valid by schema will
now be rejected by runtime loaders instead of reaching evaluation.

## Consequences

- Plugin evidence can become an auditable release decision without moving
  evaluator semantics into adapters.
- Evaluate and compare no longer diverge when custom evaluators are selected.
- Policy authors must use explicit direction and canonical metric names.
- Provider-backed evaluator determinism and plugin isolation remain external
  responsibilities.
