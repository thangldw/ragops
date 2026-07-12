# ADR 0010: Repair trace 0.4 schema JSON syntax

- Status: Accepted by product owner release request
- Date: 2026-07-12

## Context

The v1.5.0 release gate parsed every JSON Schema and found that
`schemas/trace-0.4.schema.json` was missing the closing brace for the
`retrieval.properties` object. The intended field structure is already used by
the trace loader, fixtures, and reference deployment, but the published schema
file itself could not be parsed as JSON.

## Decision

Add the missing object-closing brace and a regression test that parses every
file under `schemas/`. Do not add, remove, rename, or reinterpret any trace 0.4
field.

## Compatibility impact

This is a compatible defect correction. Runtime trace handling, schema version,
required fields, optional fields, evaluator behavior, and release-gate semantics
do not change. Consumers that previously could not load the malformed schema
can now parse it normally.

## Consequences

- All published schema files become valid JSON.
- Future malformed schema syntax fails the repository test suite.
- A separate schema-version bump is unnecessary because the contract meaning is
  unchanged.
