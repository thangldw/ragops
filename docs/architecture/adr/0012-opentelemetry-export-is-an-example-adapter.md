# ADR 0012: Keep OpenTelemetry export as an example adapter

- Status: Accepted by product owner continuation request
- Date: 2026-07-12

## Context

Teams often already record generation and retrieval work as OpenTelemetry
spans. RAGOps needs an adoption path that demonstrates how those events become
portable trace 0.4 evidence without adding an OpenTelemetry runtime dependency
or redefining the trace contract.

## Decision

Publish a dependency-free example adapter under `examples/`. It accepts
already-exported span dictionaries, maps a documented set of semantic
attributes into the existing trace 0.4 envelope, validates required values,
and writes JSONL through the existing trace writer.

The adapter does not initialize an SDK, contact a collector, inspect arbitrary
span payloads, or change core evaluation semantics. Applications remain
responsible for filtering secrets and personal data before invoking it.

## Compatibility impact

The change is additive. The trace 0.4 JSON Schema, loader, evaluator, CLI, API,
metrics, and release-gate behavior do not change.

## Consequences

- Existing OpenTelemetry users get a copyable integration example.
- The dependency-free open-source core remains unchanged.
- Provider- or SDK-specific exporters can be added later as optional plugins.
- Attribute names are an example mapping, not a new RAGOps public schema.
