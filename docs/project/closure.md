# Project closure record

## Decision

RAGOps is complete and active development is paused as of 2026-07-13. Stable
release `2.4.0`, its source, package distributions, documentation, examples,
release evidence, and GitHub Pages showcase remain public. The repository is
archived until the owner decides to resume development.

## Contract and compatibility impact

No public schema, metric meaning, release-gate behavior, CLI/API surface, or
open-core boundary changes. This closure changes repository governance and
maintenance status only; it does not publish a new package version.

## Preserved evidence

- Source, tests, scenarios, adapters, examples, and package configuration.
- Historical requirements, ADRs, release notes, and acceptance records.
- Current README visuals, public showcase assets, and published benchmark data.
- Local release tooling needed to verify a future patch without GitHub Actions.

## Cleanup performed

- Removed unreferenced intermediate design-review captures.
- Removed obsolete, unreferenced showcase screenshots.
- Removed local caches, bytecode, and operating-system metadata.
- Replaced active contribution and support expectations with archived-project
  guidance.

## Reopening checklist

1. Unarchive the GitHub repository and confirm the owner-approved user need.
2. Write a scoped product requirement; add an ADR for any public contract,
   metric, release-gate, or open-core boundary change.
3. Review supported Python versions, dependencies, workflows, documentation,
   and external service credentials for drift.
4. Run `ruff check .` and `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`, then run
   the complete local release-readiness workflow before publishing anything.
5. Update the roadmap, support policy, changelog, and project status only after
   owner acceptance.
