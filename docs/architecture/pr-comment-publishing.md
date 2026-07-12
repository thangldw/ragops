# Safe pull-request comment publishing design

## Trust boundary

```text
pull_request workflow (read-only, untrusted code)
        │ bounded Markdown artifact
        ▼
workflow_run publisher (default-branch code, write only to PR comments)
        │ verify metadata; parse as data; never execute
        ▼
one idempotent RAGOps comment + canonical workflow/artifact links
```

## Evaluation workflow

- Trigger: `pull_request`, never `pull_request_target` for evaluation.
- Permissions: `contents: read` only.
- Secrets: none.
- Output: bounded UTF-8 Markdown report, command log, head SHA, and pull-request
  number.
- Artifact names and maximum sizes are fixed by trusted workflow code.

## Publisher workflow

- Trigger: `workflow_run` for the exact evaluation workflow name.
- Code source: default branch only; do not checkout the pull request.
- Permissions: `actions: read`, `contents: read`, `pull-requests: write`.
- Verify repository, source event, workflow ID/name, completion state, head SHA,
  pull-request association, artifact name, file count, and size before parsing.
- Treat artifact bytes, branch names, titles, and report content as untrusted data.
- Never source, execute, template into shell, or deserialize executable objects
  from the artifact.
- Render through a GitHub API request with values passed as data, not shell code.

## Idempotency

Use a stable marker such as:

```text
<!-- ragops-release-gate -->
```

List comments by the bot identity, find at most one marker comment, and update
it. Create a comment only when no marker exists. Reruns therefore replace stale
evidence instead of adding noise.

## Failure behavior

- Metadata mismatch, missing artifact, oversized evidence, or ambiguous PR
  association: publish nothing and fail the publisher job.
- Evaluation BLOCK: publish the BLOCK summary, then retain the original check
  failure as the release gate.
- API failure: do not weaken or reinterpret the evaluation result.

## Implemented controls

The publisher is implemented in `.github/workflows/ragops-pr-comment.yml` and
`apps/github_pr_comment.py`. Actions are pinned to full commit SHAs. The source
gate emits a bounded manifest, while the publisher validates the event,
artifact allowlist, sizes, manifest, conclusion, PR association, and comment
cardinality before writing through the GitHub JSON API.

The current read-only summary/artifact workflow remains the canonical release
gate. The comment is reviewer visibility only and cannot change PASS/BLOCK.
