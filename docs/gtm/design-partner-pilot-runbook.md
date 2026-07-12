# Design-partner pilot runbook

## 1. Qualify and consent

- Select one recurring RAG/agent workflow and one decision owner.
- Agree on the eligible cohort, baseline/pilot dates, exclusions, targets, and
  stop conditions before collecting observations.
- Obtain the partner's approval for pseudonymous workflow measurement.
- Do not collect raw prompts, customer documents, names, emails, credentials,
  or production secrets in the RAGOps pilot files.

## 2. Establish baseline

Collect at least two weeks or 50 eligible tasks when feasible. Record one
`ragops-pilot-observation-0.1` line per eligible task, including incomplete and
unsuccessful tasks. Freeze the manifest and targets before pilot exposure.

## 3. Run the constrained pilot

- Start with synthetic or redacted evaluation fixtures.
- Keep critical external actions human-approved.
- Review critical incidents immediately; any incident forces HOLD.
- Record pilot observations using the same task definition as baseline.

## 4. Generate evidence

```bash
ragops pilot-report \
  --manifest pilot-manifest.json \
  --observations pilot-observations.jsonl \
  --economics pilot-economics.json \
  --output pilot-report.md
```

Economics are optional. Omit `--economics` when loaded labor cost or pilot
investment has not been reviewed by the partner.

## 5. Review and decide

- **SCALE:** all agreed primary targets pass and critical incidents remain zero.
- **HOLD:** technical quality is acceptable but adoption or workflow outcomes
  miss target.
- **REDESIGN:** task definition, cohort, instrumentation, or workflow needs a
  material change before another pilot.

The command emits SCALE or HOLD from the frozen target contract. The owner can
choose REDESIGN during review and must document why. Never publish an adoption
or ROI claim without the real cohort, period, denominator, exclusions,
assumptions, and partner approval.
