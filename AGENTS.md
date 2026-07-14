# RAGOps collaboration contract

RAGOps is product-first. Current requirements, architecture decisions, and
acceptance criteria are authoritative; implementation must not redefine them
silently.

## Ownership

- Thang owns product vision, architecture acceptance, release, and publication.
- Coding agents may implement, test, refactor, document, and propose decisions.
- Public schema, metric, release-gate, or open-core changes require an explicit
  decision record and owner review.

## Required workflow

1. Read `docs/product/requirements.md`, the affected architecture decisions,
   and the relevant canonical guide.
2. State user outcome, contract impact, acceptance criteria, and non-goals.
3. Implement the smallest vertical slice with proportional tests and docs.
4. Run `ruff check .` and `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`.
5. Exercise affected CLI/API paths and update `CHANGELOG.md`.
6. Leave work ready for owner acceptance. Do not tag, release, or publish unless
   explicitly authorized.

## Boundaries

- `src/ragops/`: dependency-free evaluation semantics.
- `apps/`: optional API and UI adapters.
- `scenarios/`: portable fixtures, policies, and expected evidence.
- `examples/`: reference integrations outside the core.
- `schemas/`: versioned public contracts.

The open-source core must make a complete offline release decision without a
hosted service.

## Repository skills

- `skills/ragops-feature/SKILL.md`: feature and maintenance work.
- `skills/ragops-presentation/SKILL.md`: showcase, diagrams, and demos.
- `skills/ragops-release/SKILL.md`: acceptance and release readiness.
