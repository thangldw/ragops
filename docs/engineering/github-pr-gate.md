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
      ragops-version: v2.3.0
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
- `ragops-report.md`, `ragops-command.log`, and bounded
  `ragops-evidence.json` metadata are uploaded as
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

## Optional PR comment publisher

This repository now includes `.github/workflows/ragops-pr-comment.yml`. It runs
only after the exact caller workflow completes, checks out trusted default-
branch code, validates the bounded evidence artifact, and creates or updates one
`<!-- ragops-release-gate -->` bot comment.

The publisher has `actions: read`, `contents: read`, and
`pull-requests: write`. It never checks out PR code, uses
`pull_request_target`, executes artifact content, or changes the gate result.
Copying the publisher to another repository requires changing
`RAGOPS_SOURCE_WORKFLOW` and the `workflow_run.workflows` allowlist to the exact
caller workflow name.

For a downstream repository, copy
[`docs/examples/github-pr-comment.yml`](../examples/github-pr-comment.yml) to
`.github/workflows/ragops-pr-comment.yml`. The example assumes the read-only
caller workflow has the exact top-level name `RAGOps`, matching the caller
recipe above. If it has another name, change both of these values to the same
exact string:

```yaml
on:
  workflow_run:
    workflows: ["Your exact caller workflow name"]

env:
  RAGOPS_SOURCE_WORKFLOW: Your exact caller workflow name
```

The recipe checks out publisher code from a reviewed RAGOps commit into a
separate path. It does not checkout the pull-request head, restore its cache,
execute its artifacts, or use `pull_request_target`. Keep that commit pin under
dependency review when upgrading.

GitHub must associate the source run with exactly one pull request. A fork PR
is publishable when GitHub supplies that single association; otherwise the
publisher fails closed without writing a comment. The source workflow remains
the required branch-protection check. The publisher only improves visibility
and never converts a blocked gate into a passing check.
