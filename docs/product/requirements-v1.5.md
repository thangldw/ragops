# Requirements v1.5 — adoption-first release evidence

## User story

As an AI engineer evaluating RAGOps, I want to understand the production
problem, run a credential-free example, inspect the evidence, and find a clear
extension path within five minutes so that I can decide whether to adopt or
contribute without first learning the whole repository.

## Public contract impact

- Additive CLI command: `ragops demo --output PATH [--force]`.
- Demo output fails closed when the destination already exists; `--force`
  replaces regular files atomically and rejects symlinked targets.
- No scenario, trace, report, metric, evaluator, or release-gate semantics
  change.
- Repository HEAD and future releases change from Apache-2.0 to MIT under ADR
  0009. Previously published releases keep their original license.
- Showcase information architecture and contributor documentation change; the
  application/API contracts do not.

## Acceptance criteria

1. `ragops demo` runs without credentials or network access, returns zero, and
   creates scenario, baseline, candidate, Markdown, and HTML evidence files.
2. The generated candidate is intentionally blocked and the summary says why.
3. Existing or symlinked output cannot be overwritten accidentally; explicit
   replacement is limited to regular files through `--force`.
4. The showcase answers problem, solution, demo, evidence, architecture,
   limitations, and next-step questions without mixing the 4-case reference
   experiment with the 30-case synthetic benchmark.
5. Desktop and mobile layouts have no horizontal page overflow; primary links
   and keyboard focus remain usable.
6. License text, package metadata, README, showcase, changelog, and ADR agree on
   MIT for repository HEAD and future releases.
7. Contributor paths include a development setup, first contribution flow,
   support guidance, conduct policy, and structured bug report.

## Non-goals

- Publishing to PyPI or creating a new GitHub release.
- Claiming semantic correctness, production security, adoption, or ROI.
- Adding automatic entity extraction, enterprise identity, or a hosted control
  plane.
- Changing metric definitions or public JSON schemas.
