# ADR 0014: Separate PR evaluation from comment publication

- Status: Accepted for bounded implementation
- Date: 2026-07-13

## Context

Pull-request comments improve reviewer visibility but require write permission.
Fork pull requests and their artifacts are untrusted. Combining evaluation of
PR code with a write token creates an avoidable privilege boundary failure.

## Decision

Keep the existing `pull_request` evaluation workflow read-only. A future
publisher may run from the default branch on `workflow_run` with only
`actions: read`, `contents: read`, and `pull-requests: write`.

The publisher must verify the source workflow identity, repository, event,
conclusion, head SHA, and pull-request number through GitHub APIs. It may parse
bounded Markdown evidence as data but must never checkout PR code, execute an
artifact, restore an untrusted cache, interpolate untrusted strings into shell,
or use `pull_request_target` to run fork code.

Comments must use a stable hidden marker and update one existing bot comment
instead of appending duplicates. The canonical workflow run and artifact remain
the source of truth.

## Compatibility impact

The reusable gate stays read-only and adds only a bounded evidence manifest.
The owner authorized the separate publisher implementation on 2026-07-13.
Permission regression tests and bounded artifact parsing remain mandatory.

## Consequences

- Reviewers get a concrete path to PR-native evidence without weakening the
  current workflow.
- The privileged publisher treats all upstream artifacts as untrusted data.
- Comment publication is allowed only through the isolated publisher described
  here; failure must not weaken or reinterpret the release decision.
