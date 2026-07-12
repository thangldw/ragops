# ADR 0008: Local team review workflow before hosted control plane

- Status: Accepted
- Date: 2026-07-12

## Context

Teams need accepted baselines, reviewer decisions, and trends, but introducing
multi-tenancy and production identity before design-partner validation creates
security and product risk.

## Decision

Extend the local SQLite store with review status, reviewer, note, and metric
trend queries. Expose the workflow through CLI, optional authenticated API, and
the browser workbench. Keep hosted tenancy outside this milestone.

## Consequences

Small teams can practice the review loop now, existing stores migrate in place,
and the hosted boundary can be designed from observed collaboration needs.

