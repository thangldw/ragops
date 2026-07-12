# Engineering handbook

## Principles

- Prefer explicit contracts over framework magic.
- Keep evaluation semantics deterministic and testable by default.
- Make metric names precise; never imply semantic validity from lexical checks.
- Add provider dependencies only behind optional adapters.
- Optimize for reviewer comprehension before abstraction count.

## Change shape

A feature change should include the requirement, model/contract, implementation,
unit and integration tests, user documentation, and changelog entry. Avoid broad
AI-generated rewrites that mix behavior, formatting, and architecture changes.

## Public compatibility

Treat Python exports, CLI flags and exit codes, JSON Schemas, report fields, and
metric meanings as public surfaces. Incompatible changes require a new schema
or major version and a migration note.

## Local verification

```bash
ruff check .
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
ragops evaluate --scenario scenarios/japanese_troubleshooting/scenario.json \
  --responses scenarios/japanese_troubleshooting/sample_responses.json
```

