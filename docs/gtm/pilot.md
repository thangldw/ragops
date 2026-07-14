# Design-partner pilot

## Decision

Determine whether a reviewed workflow shows repeat use, improved task outcomes,
acceptable safety, and credible time/cost evidence without mixing observations
with assumptions.

## Data contract

Use one pseudonymous observation per eligible baseline or assisted task. Record
pilot and phase, task and user IDs, completion, success, duration, critical
incidents, reviewer disagreement, and optional measured cost. Do not collect raw
prompts, customer documents, production credentials, or direct identifiers.

```bash
ragops pilot-report \
  --manifest docs/gtm/pilot-fixtures/synthetic-manifest.json \
  --observations docs/gtm/pilot-fixtures/synthetic-observations.jsonl \
  --economics docs/gtm/pilot-fixtures/synthetic-economics.json \
  --output pilot-report.md
```

## Metrics

- Eligible users and tasks, activation, and repeat usage.
- Baseline and assisted task-success rates and uplift.
- Median duration and estimated time saved.
- Critical incidents and reviewer disagreement.
- Measured cost separated from hourly-cost and pilot-investment assumptions.

## Guardrails

Obtain consent, minimize data, define the observation window and denominators,
review exclusions, and stop on a critical incident. The deterministic report is
observational evidence, not causal proof. The bundled synthetic fixtures are a
rehearsal and must never be described as customer adoption or ROI.
