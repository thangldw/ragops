# RAGOps collaboration contract

This repository is product-first. Product intent, contracts, and acceptance
criteria are authoritative; implementation must not silently redefine them.

## Ownership

- Thang owns product vision, architecture acceptance, review, and release.
- Codex and Claude Code may implement, test, refactor, and propose ADRs.
- Any change to a public schema, release gate, metric meaning, or open-core
  boundary requires an ADR and explicit owner review.

## Required workflow

1. Read the relevant product requirement and architecture decision.
2. State the contract being changed and its compatibility impact.
3. Implement the smallest vertical slice, including tests and documentation.
4. Run `ruff check .` and `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`.
5. Update the changelog for user-visible behavior.
6. Leave the work ready for owner acceptance; do not publish or release unless
   explicitly requested.

## Architectural boundaries

- `src/ragops/` is the dependency-free evaluation core.
- `apps/` contains adapters and user interfaces, not evaluation semantics.
- `scenarios/` contains portable fixtures, policies, and expected evidence.
- Provider integrations are optional adapters or plugins.
- The open-source core must remain valuable without a hosted service.

## Repository skills

- Use `skills/ragops-feature/SKILL.md` for feature implementation.
- Use `skills/ragops-release/SKILL.md` for validation and release readiness.
- Use `skills/ragops-presentation/SKILL.md` for demos and presentation assets.

