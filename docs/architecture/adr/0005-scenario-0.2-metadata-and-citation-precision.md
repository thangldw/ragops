# ADR 0005: Scenario 0.2 metadata and citation precision

- Status: Accepted
- Date: 2026-07-12

## Context

Scenario 0.1 can express evidence and citation completeness but cannot describe
benchmark coverage or distinguish correct citations from extra unsupported
citations.

## Decision

Scenario 0.2 adds an optional citation-precision threshold and per-case
category, severity, language, tags, and attack-category metadata. The engine
continues to read 0.1 with safe defaults. Citation coverage retains its existing
meaning; citation precision is added as a separate metric.

## Consequences

Existing scenarios remain valid. New benchmark reports can segment cases and
detect citation stuffing. Published 0.1 schema and semantics remain unchanged.

