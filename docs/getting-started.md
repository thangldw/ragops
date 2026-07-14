# Getting started

RAGOps evaluates a RAG or AI agent you already operate. It does not build the
retriever, generator, or orchestration layer.

## 1. Run the credential-free proof

```bash
python -m venv .venv
source .venv/bin/activate
pip install ragops==2.4.0
ragops demo --output ragops-demo
```

Open `ragops-demo/release-report.html`. The accepted baseline passes and the
intentionally regressed candidate is blocked with named reasons. The bundle
contains the scenario, fixtures, JSON, Markdown, and standalone HTML evidence.

## 2. Evaluate recorded responses

```bash
ragops evaluate \
  --scenario path/to/scenario.json \
  --responses path/to/responses.json \
  --format markdown \
  --output evaluation.md
```

Use `--traces` for portable JSONL trace 0.4 records.

## 3. Compare candidate with baseline

```bash
ragops compare \
  --scenario path/to/scenario.json \
  --baseline path/to/baseline.json \
  --candidate path/to/candidate.json \
  --evaluation-policy path/to/evaluation-policy.toml \
  --format html \
  --output release-report.html
```

- Exit `0`: candidate passes.
- Exit `2`: policy blocks the candidate.
- Other non-zero: input, configuration, installation, or contract error.

## 4. Integrate the gate

- [CI and pull-request gates](engineering/ci-gates.md)
- [Trace, provider, and external-metric adapters](engineering/integrations.md)
- [Evaluator and release-policy strategy](evaluation/strategy.md)
- [Testing and release workflow](engineering/testing-and-release.md)

## Optional local workbench

```bash
RAGOPS_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" \
  docker compose up --build
```

Open <http://localhost:8000> and enter the same API key. Compose binds to
localhost; the workbench is an adapter over the same core contract.

## Evidence boundary

Synthetic fixtures prove repeatability and expected gate behavior only. Replace
them with reviewed, consented evidence from your workflow before making
production, adoption, security, or ROI claims.
