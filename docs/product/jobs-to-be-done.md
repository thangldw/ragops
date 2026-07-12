# Jobs to be done and use cases

## Core job

When an AI workflow changes, evaluate the candidate against a versioned
scenario and accepted baseline so the team can make an explainable release
decision before production users encounter a regression.

## Priority use cases

1. **Pull-request gate:** compare recorded candidate traces with a baseline and
   post a compact quality, safety, latency, and cost report.
2. **Pilot acceptance:** translate customer success criteria into cases,
   thresholds, and critical policies before recommending scale-up.
3. **Incident reproduction:** preserve the failed interaction as a regression
   case and prevent recurrence.
4. **Evaluator experimentation:** add a deterministic or provider-backed plugin
   without coupling it to the runner.
5. **Governance evidence:** export the scenario version, result, findings, and
   decision in a portable format.

## Product guardrails

- RAGOps evaluates applications; it does not own retrieval or generation.
- A model-based judge may add evidence but must not hide deterministic results.
- Aggregate quality cannot override a critical policy failure.
- Recorded and synthetic data are first-class so evaluation can run offline.

