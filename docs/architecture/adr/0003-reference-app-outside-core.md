# ADR 0003: Keep reference applications outside the evaluation core

- Status: Accepted
- Date: 2026-07-12

## Context

The FDE showcase needs a real RAG or agent deployment, but RAGOps aims to remain
provider-neutral evaluation infrastructure.

## Decision

Reference applications live under `examples/` or a separate repository and
communicate through the portable trace contract. Retrieval, generation, and
tool execution are not added to `src/ragops/`.

## Consequences

The core stays small and reusable. End-to-end demos require an additional
component, and trace-contract quality becomes a critical integration surface.

