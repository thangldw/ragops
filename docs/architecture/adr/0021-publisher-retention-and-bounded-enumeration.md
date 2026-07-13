# ADR 0021: Bound publisher enumeration without owning retention

- Status: Accepted for owner review
- Date: 2026-07-13

## Context

The pull-request comment publisher reads GitHub Actions artifacts and issue
comments across a write-enabled trust boundary. GitHub may return expired
artifacts, paginated collections, or rate-limit responses. Artifacts and bot
comments also have different repository-owned retention lifecycles.

## Decision

Keep enumeration bounded and fail closed. One artifact response may contain at
most the first 100 records and must report a matching `total_count`; otherwise
the publisher writes nothing. Comment discovery reads at most ten 100-item
pages and writes nothing when that bound cannot prove marker uniqueness. HTTP
failures, including rate limits, remain contract errors and never change the
evaluation result.

RAGOps does not automatically delete evidence artifacts or pull-request
comments. Artifact retention remains controlled by the adopting repository's
Actions retention setting. The publisher updates its single marker comment;
repository owners retain authority to remove comments under their own audit and
data-retention policy.

## Compatibility impact

This records existing adapter behavior and adds deterministic negative coverage.
It does not change evaluation schemas, metrics, PASS/BLOCK semantics, workflow
permissions, or the dependency-free core.

## Consequences

- Large or ambiguous collections require owner cleanup or a future reviewed
  pagination contract before publication can resume.
- Rate limiting delays comment visibility but cannot weaken the canonical gate.
- Adopting repositories must choose Actions retention and comment-deletion
  policy appropriate to their audit requirements.
- No deletion token, scheduled cleanup job, or hosted retention service is
  added to the open-source project.
