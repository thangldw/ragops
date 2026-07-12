# Design-partner pilot measurement plan

This plan is implemented by the dependency-free `ragops pilot-report` command.
The bundled fixtures are synthetic; replace them only with consented,
pseudonymous design-partner observations.

## Decision and cadence

- Decision: scale, hold, or redesign one constrained workflow pilot.
- Review cadence: weekly operating review plus a final baseline/pilot readout.
- Owners: one technical owner and one workflow/business owner.
- Primary KPIs: repeat usage, task-success uplift, and time saved.
- Guardrail: zero critical permission, action, or data incidents.

## Baseline period

Measure at least two weeks or 50 eligible tasks before exposing recommendations:

- Median and p90 time-to-answer.
- Escalation rate and escalation precision.
- Manual search steps per task.
- Successful task completion and reviewer disagreement.
- Current tooling and review hours per release.

## Pilot metrics

- Weekly active eligible users and repeat usage.
- Accepted-answer/task-success rate.
- Citation precision and unsupported-claim reports.
- Permission/action incidents, with a zero-tolerance critical guardrail.
- Cost per successful task and evaluation time per release.

RAGOps calculates the following operational definitions:

- **Activation rate:** distinct eligible users with at least one completed pilot
  task divided by all pseudonymous eligible users in the manifest.
- **Repeat usage rate:** activated users with completed tasks in at least two ISO
  weeks divided by activated users.
- **Task-success uplift:** pilot successful/completed rate minus the equivalent
  baseline rate.
- **Time-saved rate:** positive difference between baseline and pilot median
  duration divided by baseline median duration.
- **Estimated time saved:** median duration difference multiplied by completed
  pilot tasks. This is derived, not directly observed per paired task.
- **Critical incidents:** count during completed pilot tasks; target is zero.
- **Reviewer disagreement:** pilot tasks marked as disputed divided by completed
  pilot tasks.
- **Observed cost:** sum of per-task pilot costs supplied by the partner.

Economic estimates are optional. When provided, gross value equals estimated
time saved times an explicit loaded hourly cost. Net value subtracts observed
pilot cost and explicit pilot investment; ROI divides net value by those costs.
These values are assumptions-driven estimates, not measured revenue.

## Run the synthetic rehearsal

```bash
ragops pilot-report \
  --manifest docs/gtm/pilot-fixtures/synthetic-manifest.json \
  --observations docs/gtm/pilot-fixtures/synthetic-observations.jsonl \
  --economics docs/gtm/pilot-fixtures/synthetic-economics.json \
  --output pilot-report.md
```

For a real pilot, set `synthetic` to `false`, record `consent_status` as
`approved`, use pseudonymous identifiers, and remove raw prompts, documents,
emails, names, and credentials before collection.

## Decision rule

Scale only when offline release gates hold, critical incidents remain zero, and
workflow improvement exceeds the target agreed during discovery. Hold when
quality passes but adoption or task outcomes do not improve.

## Evidence discipline

Separate measured outcomes, estimates, and user anecdotes. Do not publish a
percentage improvement until the denominator, cohort, period, and exclusions
are documented.

The generated report is observational before/after evidence and does not prove
causality. Keep the manifest, observations, assumptions, generated report, and
owner decision together for review.
