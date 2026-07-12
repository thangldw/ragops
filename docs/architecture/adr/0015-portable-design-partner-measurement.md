# ADR 0015: Portable design-partner measurement evidence

- Status: Accepted for implementation
- Date: 2026-07-13

## Context

RAGOps has synthetic quality evidence but no contract for collecting design-
partner adoption and workflow outcomes. Mixing observed task data, estimates,
and anecdotes would make ROI claims difficult to audit.

## Decision

Add a dependency-free pilot observation contract and deterministic report to
the open-source core. One record represents one eligible baseline or assisted
task and uses a pseudonymous user identifier. Reports separate measured task
outcomes and costs from economic assumptions supplied in a distinct file.

Primary decision metrics are repeat usage, task-success uplift, and time saved.
Critical incidents are a zero-tolerance guardrail; reviewer disagreement and
eligible-task coverage remain diagnostic. Estimated net value and ROI are shown
only when hourly cost and pilot investment assumptions are explicitly supplied.

## Compatibility impact

This is an additive schema and CLI capability. It does not change evaluation
reports, existing metric definitions, release gates, provider adapters, or the
open-core boundary.

## Consequences

- A design partner can run the measurement workflow offline without telemetry
  infrastructure or provider credentials.
- The same input produces the same Markdown report.
- The report is observational evidence, not causal proof.
- Public adoption claims still require owner review of real cohort, period,
  denominator, exclusions, and consent.
