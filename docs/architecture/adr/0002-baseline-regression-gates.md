# ADR 0002: Baseline-aware regression gates

Status: Accepted

## Context

Absolute thresholds answer whether a build meets a minimum bar, but do not
show whether it became materially worse than the accepted version. Teams need
both signals during code review.

## Decision

Evaluate baseline and candidate independently, then apply a separate regression
policy to metric deltas. Candidate absolute failure is always a comparison
failure. A new critical finding is never absorbed by aggregate averages.

## Consequences

- Reports can explain both absolute readiness and relative change.
- Baseline artifacts must be versioned with the application or scenario.
- Default tolerances remain conservative and can be customized through Python.
- Statistical significance and noisy online metrics remain future work.

