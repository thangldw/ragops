# M4 acceptance — local team workflow

## Decision

**Accepted as a single-workspace collaboration layer.** It is not a hosted,
multi-tenant control plane.

## Evidence

- SQLite migration adds review status, reviewer, and note without dropping runs.
- CLI supports run history, review decisions, and metric trends.
- Optional API exposes runs, trends, and review writes behind the existing key.
- Browser workbench displays evaluation results and saved experiment history.
- Nightly workflow gates the benchmark and reference deployment.
- Automated tests cover review validation, missing runs, migration behavior, and
  ordered metric trends.

## Deferred to hosted product

- Workspace/tenant isolation, SSO/RBAC, audit immutability, encryption policy,
  managed database, queues, scheduled suite management, and notifications.

