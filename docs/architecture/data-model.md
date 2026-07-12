# Data model

## Scenario

A versioned evaluation policy containing identity, thresholds, red-team rules,
and cases. A case contains a user question, trusted evidence, and required
citation identifiers.

## Recorded response / trace

An application observation keyed to a case: answer, citations, retrieval IDs,
latency, cost, and human-approval state. Future compatible extensions should
carry build, model, prompt, retriever, and environment metadata.

## Case result

Per-case deterministic and plugin metrics plus findings. Findings have a rule,
severity, and human-readable explanation.

## Evaluation report

Aggregate metrics, failed absolute gates, case results, scenario identity, and
metadata. A comparison report contains baseline and candidate reports, deltas,
and regression gates.

## Invariants

- Case IDs are unique within a scenario.
- Response coverage exactly matches scenario cases.
- Identical deterministic inputs yield identical evaluation content.
- Critical findings block release regardless of aggregate averages.
- Published schema versions are immutable.

