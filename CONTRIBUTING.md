# Contributing to RAGOps

RAGOps welcomes small, evidence-backed contributions. Good first changes are
usually a scenario case, evaluator test, report improvement, documentation
example, or focused integration fixture.

Read the [Code of Conduct](CODE_OF_CONDUCT.md) and never submit customer data,
secrets, credentials, private traces, or proprietary prompts.

## First contribution

1. Choose an issue labeled `good first issue` or open a focused proposal.
2. Fork the repository and create a branch.
3. Set up the development environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e '.[dev,api]'
   ragops demo --output /tmp/ragops-demo
   ```

4. Make the smallest vertical change, including tests and documentation.
5. Run the required checks:

   ```bash
   ruff check .
   PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
   ```

6. Open a pull request that explains the user impact, evidence, limitations,
   and compatibility effect.

## Architecture boundary

- `src/ragops/` is the dependency-free evaluation core.
- `apps/` contains adapters and user interfaces, not evaluation semantics.
- `scenarios/` contains portable fixtures, policies, and expected evidence.
- Provider integrations remain optional adapters or plugins.

Do not silently change metric meaning, public JSON fields, release-gate
behavior, plugin protocols, or the open-source boundary. Those changes require
an ADR, compatibility note, tests, and owner acceptance.

## Add an evaluator

Implement `CaseEvaluator` with a globally unique `name`. Keep it deterministic
unless the provider, model, prompt, and sampling configuration are recorded in
report metadata. Add unit tests for the score, a negative case, and a small
integration fixture.

Use `critical` findings only when they must block release regardless of
aggregate metrics. Explain that policy choice in the pull request.

## Add a scenario or attack case

- Use synthetic or redacted evidence.
- Give every case a stable ID and explicit expected citations.
- State the category, severity, language, and attack metadata where relevant.
- Add coverage assertions when extending a published benchmark taxonomy.

## Pull-request checklist

- [ ] Product requirement and relevant ADRs were read.
- [ ] Public contract impact and non-goals are stated.
- [ ] Tests cover expected and failure behavior.
- [ ] Ruff and the full test suite pass.
- [ ] Documentation and changelog reflect user-visible behavior.
- [ ] No secrets, private data, generated databases, or customer artifacts are included.

For usage questions and support expectations, see [SUPPORT.md](SUPPORT.md).
