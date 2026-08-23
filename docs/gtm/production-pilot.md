# Production pilot evidence runbook

This runbook turns approved design-partner observations into reviewable RAGOps adoption evidence. It does not create production evidence by itself and does not treat synthetic fixtures, downloads, repository traffic, or CLI event counts as adoption.

## Entry criteria

- The design partner has approved the pilot purpose, measurement period, retention, and pseudonymous identifiers.
- A named owner controls the manifest, observation file, economics assumptions, and final review.
- Baseline and pilot tasks use the same eligibility rules and success rubric.
- Prompts, traces, customer content, emails, names, and account identifiers remain outside the pilot files.

## Measurement contract

Use `schemas/pilot-manifest-0.1.schema.json` for cohort and targets, `schemas/pilot-observation-0.1.schema.json` for one task observation per JSONL line, and `schemas/pilot-economics-0.1.schema.json` for optional estimates. Production manifests set `synthetic` to `false` and `consent_status` to `approved`.

Collect at least one completed baseline and pilot task, using unique task IDs. Record duration, task success, critical incidents, reviewer disagreement, and observed cost. RAGOps derives activation, repeat usage, task-success uplift, median time saved, incident count, disagreement rate, and optional ROI estimates from those explicit observations.

## Generate the evidence

```bash
ragops pilot-report \
  --manifest controlled/pilot-manifest.json \
  --observations controlled/pilot-observations.jsonl \
  --economics controlled/pilot-economics.json \
  --output controlled/pilot-report.md
```

Review the cohort, denominators, exclusions, consent, source files, failed conditions, and economic assumptions before sharing the result. A `SCALE` decision means the declared observational targets passed; it does not establish causality.

## Usage boundaries

`RAGOPS_USAGE_LOG` is optional local product-operation evidence. It contains only timestamp, version, top-level command, and exit code, so it cannot prove task success, repeat user adoption, or production impact. The skills-only ChatGPT plugin does not expose install or usage counts to this repository. Keep those platform metrics separate and label unavailable values as unavailable.

## Publication gate

Publish a case study only when the design partner approves the exact aggregate claims and no small-cohort cell can re-identify a person. Label observational results as production-derived, keep economic figures as estimates, disclose limitations, and retain the reviewed source bundle under the agreed retention policy.
