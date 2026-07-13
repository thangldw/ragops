# ADR 0018: Portable external metric envelope

- Status: Accepted for implementation
- Date: 2026-07-13
- Owner authorization: continued staged implementation and release requested by
  Thang on 2026-07-13

## Context

RAGOps should compete as a portable release-policy and evidence layer rather
than by recreating every evaluator in Ragas, DeepEval, Langfuse, or private
model-quality stacks. Native export formats are dependency-specific and change
outside RAGOps release control.

## Decision

Define one versioned JSON envelope containing a provider identifier and one
finite numeric metric map per scenario case. A dependency-free adapter exposes
that envelope through the existing `CaseEvaluator` protocol. Aggregate metric
keys are namespaced as `<provider>.<metric>` and therefore work with the v2.0
evaluation policy without special gate logic.

Evaluate requires exact scenario coverage. Compare uses distinct baseline and
candidate envelopes, requires the same provider and per-case metric sets, and
then reports ordinary aggregate deltas. RAGOps never changes metric direction,
scale, calibration, or meaning; the policy author owns those decisions.

Framework integrations should export into this stable envelope outside the
core. Native format parsers may be optional adapters in the future, but cannot
silently redefine the canonical envelope.

## Compatibility impact

The envelope, adapter, and CLI options are additive. Omitted external metrics
preserve existing reports and decisions. Report schema already permits numeric
metric and delta keys.

## Consequences

- Teams can reuse existing evaluator investments while centralizing release
  governance in RAGOps.
- Framework upgrades do not force changes to the dependency-free core.
- Metric comparability and calibration remain explicit owner responsibilities.
