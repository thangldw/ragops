# GitHub pull-request release gate

RAGOps ships a reusable, read-only workflow that compares a candidate response
fixture with an accepted baseline. It publishes the Markdown report to the job
summary, uploads the report and command log, then preserves the CLI decision:
exit `0` passes and exit `2` blocks the pull request.

## Caller workflow

Create `.github/workflows/ragops.yml` in the adopting repository:

```yaml
name: RAGOps

on:
  pull_request:
    paths:
      - "evals/**"
      - ".github/workflows/ragops.yml"

jobs:
  release-gate:
    uses: thangldw/ragops/.github/workflows/ragops-gate.yml@main
    with:
      ragops-version: v1.5.0
      scenario: evals/scenario.json
      baseline: evals/baseline.json
      candidate: evals/candidate.json
      policy: evals/ragops.toml
```

Use `@main` while the reusable workflow is in development. For a production
repository, pin the workflow reference to a reviewed commit SHA or the first
release tag that contains it. The `ragops-version` input independently pins the
installed evaluator package.

## Evidence behavior

- `ragops-report.md` is appended to `$GITHUB_STEP_SUMMARY` even when the gate
  blocks the candidate.
- `ragops-report.md` and `ragops-command.log` are uploaded as
  `ragops-release-evidence`.
- Contract errors create an error report and fail after evidence upload.
- The reusable workflow requests only `contents: read` and does not comment on
  pull requests or write to the caller repository.

## Branch protection

After the caller workflow has run once, require its `release-gate` job in the
repository branch-protection rules. Keep scenario, baseline, and policy changes
reviewable because changing the release contract can make a regression appear
acceptable.

## Local parity

Run the same decision before pushing:

```bash
ragops compare \
  --scenario evals/scenario.json \
  --baseline evals/baseline.json \
  --candidate evals/candidate.json \
  --policy evals/ragops.toml \
  --format markdown \
  --output ragops-report.md
```

The workflow is an adapter only. Metric definitions and release semantics stay
inside the dependency-free core.
