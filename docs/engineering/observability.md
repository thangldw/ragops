# Observability contract

RAGOps distinguishes application telemetry from evaluation evidence.

## Required trace fields

- Case and application-run identity.
- Output answer and citations.
- Retrieved document identifiers.
- End-to-end latency and estimated cost.
- Human approval state for consequential actions.

## Planned metadata

- Model/provider and generation parameters.
- Prompt, retriever, index, dataset, and application build versions.
- Token usage and step-level latency.
- Tool calls, authorization decision, and execution outcome.

## Privacy

Trace exporters should support field allow-lists and redaction before data
leaves the evaluated application. Raw prompts, evidence, or user identifiers
must not be assumed safe to retain.

