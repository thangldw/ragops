# ADR 0011: Keep the reusable PR gate outside evaluation semantics

- Status: Accepted by product owner continuation request
- Date: 2026-07-12

## Context

Teams need to run RAGOps on pull requests without copying a long sequence of
setup, comparison, report, artifact, and exit-code steps. The integration must
not make GitHub Actions the owner of evaluation behavior or weaken the
dependency-free core.

## Decision

Publish a reusable workflow as an adapter. It installs a selected RAGOps
revision, checks out caller-owned fixtures, invokes the existing CLI, preserves
its exit code, and exposes generated evidence through Step Summary and an
artifact. It contains no evaluator or release-policy semantics.

The workflow uses read-only repository permissions and does not post pull
request comments. Inputs are passed into shell commands through quoted
environment variables.

## Compatibility impact

The workflow is additive. Public Python, CLI, API, JSON Schema, report, metric,
and release-gate contracts do not change.

## Consequences

- Adopters get a short, reviewable integration path.
- Caller repositories retain ownership of scenarios, baselines, candidates,
  and branch protection.
- Comment automation can be proposed later with a separate permission and fork
  threat-model review.
