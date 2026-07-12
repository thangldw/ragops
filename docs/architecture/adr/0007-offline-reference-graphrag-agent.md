# ADR 0007: Offline deterministic GraphRAG-style reference agent

- Status: Accepted
- Date: 2026-07-12

## Context

M2 needs an end-to-end application that emits real traces while the open-source
quick start must remain credential-free and reproducible.

## Decision

Build a reference Japanese troubleshooting agent with role filtering, lexical
retrieval, explicit graph expansion, authority/intent ranking, controlled
workflow decisions, and trace 0.4 export. Treat an LLM generator as a future
optional adapter rather than an M2 dependency.

## Consequences

The integration and regression story is reproducible in CI. The application is
clearly labeled as a reference architecture and cannot be presented as evidence
of production model quality or automatic GraphRAG extraction.

