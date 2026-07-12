# Requirements v1.8 — review visibility and measured adoption

## User stories

1. As a pull-request reviewer, I want one current RAGOps comment so that the
   release decision and canonical evidence are visible without opening logs.
2. As a repository owner, I want comment publication isolated from untrusted PR
   execution so that reviewer convenience does not grant write access to PR code.
3. As a design partner, I want a portable pilot observation contract and report
   so that adoption, task outcomes, safety, time saved, and estimated economics
   can be reviewed without a hosted service.
4. As a product owner, I want measured outcomes separated from assumptions so
   that synthetic fixtures cannot be presented as customer ROI.

## Public contract impact

- Add a bounded `ragops-evidence.json` manifest to the existing GitHub release
  evidence artifact. Existing report and command-log files remain unchanged.
- Add a default-branch `workflow_run` publisher with only `actions: read`,
  `contents: read`, and `pull-requests: write` permissions.
- Add pilot observation schema 0.1 and `ragops pilot-report` for deterministic
  JSONL aggregation and Markdown evidence.
- Additive only: evaluation schemas, evaluator semantics, API, comparison
  policy, and PASS/BLOCK behavior do not change.

## Acceptance criteria

1. The publisher verifies repository, workflow name, source event, completion,
   run ID, head SHA, exactly one PR, artifact identity, file allowlist, file
   sizes, manifest values, and UTF-8 before publishing.
2. Artifact content is parsed as data only; no PR checkout, cache restore,
   shell interpolation, `pull_request_target`, or artifact execution is used.
3. One marker comment is created or updated idempotently. Ambiguous marker
   comments, artifacts, or PR associations fail closed.
4. Evaluation BLOCK remains a failing check while its summary can still be
   published to the PR.
5. Pilot input records phase, pseudonymous user, task outcome, duration,
   critical incidents, reviewer disagreement, and optional cost.
6. The pilot report calculates cohort/task counts, activation, repeat usage,
   task-success uplift, time saved, incidents, disagreement, measured cost, and
   optional estimated net value/ROI with explicit assumptions.
7. Missing cohorts, invalid values, duplicate task observations, division by
   zero, and mixed pilot IDs fail with actionable contract errors.
8. Synthetic fixtures and generated reports are visibly labeled synthetic.
9. Unit, negative, workflow-contract, CLI, lint, and full-suite tests pass.

## Non-goals

- Posting comments from the reusable workflow itself.
- Executing or rendering arbitrary files from PR artifacts.
- Supporting multiple PRs per workflow run.
- Collecting PII, raw prompts, customer documents, or production credentials.
- Claiming design-partner adoption or ROI before reviewed real observations exist.
- Hosted analytics, billing, causal inference, or automated customer outreach.
