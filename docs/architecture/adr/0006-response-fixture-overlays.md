# ADR 0006: Response fixture overlays

- Status: Accepted
- Date: 2026-07-12

## Context

Storing a full 30-case response set for every regression or attack duplicates
unchanged data, obscures failure intent, and allows fixtures to drift.

## Decision

Response fixture 0.2 may extend a local baseline and override selected response
fields by case ID. Paths resolve relative to the overlay file. Cycles, duplicate
overrides, unknown cases, and unknown fields are rejected.

## Consequences

Reviewers can see exactly what changed in a candidate. The loader performs local
file composition, while evaluation still receives the same immutable response
objects and remains deterministic.

