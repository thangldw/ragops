# Contributing

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,api]'
pytest
ruff check .
```

## Change contract

Every product requirement must resolve to code, configuration, tests, or
documentation. Changes to public JSON fields, CLI arguments, plugin protocols,
or report semantics require an ADR and a compatibility note.

## Pull requests

- Keep one product decision per pull request where practical.
- Add tests for behavior and failure modes.
- Run the sample regression comparison locally.
- Do not commit customer data, secrets, generated reports, or databases.
- Explain user impact and migration requirements in the description.

## Evaluator plugins

Implement `CaseEvaluator` with a globally unique `name`. Evaluators must be
deterministic unless their provider, model, prompt, and sampling configuration
are recorded in report metadata. Findings should use `critical` only when they
must block release regardless of aggregate scores.

