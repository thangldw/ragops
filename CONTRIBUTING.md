# Contributing

RAGOps accepts focused, owner-reviewed fixes and product slices. Start with a
GitHub issue or discussion that states the user outcome and compatibility
boundary before opening an implementation pull request.

Never submit customer data, secrets, credentials, private traces, or proprietary
prompts. Follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,api]'
ragops demo --output /tmp/ragops-demo
```

## Change workflow

1. Read [the current requirement](docs/product/requirements.md) and
   [architecture decisions](docs/architecture/decisions.md).
2. State public contract impact and non-goals.
3. Implement the smallest vertical slice with expected and failure tests.
4. Run:

   ```bash
   ruff check .
   PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
   ```

5. Exercise the affected CLI/API path and update the canonical guide plus
   `CHANGELOG.md`.
6. Describe evidence, limitations, and the owner decision requested in the PR.

## Architecture rules

- Keep `src/ragops/` dependency-free.
- Put UIs and service adapters in `apps/`.
- Put portable fixtures and policies in `scenarios/`.
- Put reference applications and provider mappings in `examples/` or adapters.
- Require an explicit decision and owner review for schema, metric, gate, or
  open-core changes.

## Evidence rules

- Use synthetic or redacted fixtures with stable case IDs.
- Keep deterministic checks visible before optional model judges.
- Use `critical` only for findings that must block regardless of averages.
- Do not claim semantic correctness, security, adoption, or ROI from synthetic
  evidence.

For usage questions see [SUPPORT.md](SUPPORT.md); report vulnerabilities through
[SECURITY.md](SECURITY.md).

## Good first contributions

These open issues are intentionally bounded for a first contribution:

1. [Add a retrieval-poisoning Failure Zoo specimen](https://github.com/thangldw/ragops/issues/22).
2. [Add a Phoenix recorded-score adapter example](https://github.com/thangldw/ragops/issues/23).
3. [Verify the no-clone demo on Windows](https://github.com/thangldw/ragops/issues/24).

Comment on the issue before starting so the owner can confirm the fixture and
expected gate.
