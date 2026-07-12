# ADR 0001: Local-first dependency-free core

Status: Accepted

## Decision

Implement scenario contracts, evaluators, release gates, and reports with the
Python standard library. Expose optional adapters for FastAPI and future model
providers.

## Consequences

- CI and local use require no external service or API key.
- Core behavior is easy to test and embed.
- The initial groundedness metric is deliberately simple and must be labeled
  as lexical evidence support.
- Advanced evaluators must implement stable interfaces instead of leaking
  provider-specific concepts into the domain model.

