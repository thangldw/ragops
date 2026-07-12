# Product requirements — v0.2

## User story

As an AI engineer reviewing a pull request, I want to compare a candidate AI
build with an accepted baseline so that CI reports meaningful regressions
instead of only checking static thresholds.

## Functional requirements

1. Evaluate baseline and candidate responses with the same scenario.
2. Calculate deltas for quality, latency, cost, and critical findings.
3. Apply explicit regression tolerances.
4. Fail when a candidate fails its absolute release gate.
5. Export JSON for automation and Markdown for human review.
6. Publish machine-readable JSON Schemas for portable contracts.

## Default regression policy

| Metric | Allowed regression |
| --- | ---: |
| Citation coverage | 0 |
| Citation precision | 0 |
| Lexical groundedness | 0.05 |
| Average latency | +250 ms |
| Average cost | +$0.005 |
| Critical findings | 0 new findings |

The Python API accepts a custom `RegressionPolicy`. CLI policy configuration is
deferred until the policy file format is stabilized.

## Acceptance criteria

- Identical baseline and candidate pass.
- Missing required citations fail the comparison.
- New critical findings fail the comparison.
- Markdown output includes baseline, candidate, delta, and failed gates.
- Existing v0.1 evaluation behavior remains compatible.
