# RAGOps 1.0

RAGOps is an open evaluation and red-team harness for production RAG and agent
systems. It turns product quality requirements into versioned scenarios,
repeatable checks, machine-readable reports, and release gates.

This repository is intentionally product-first: the reference scenario is a
Japanese enterprise troubleshooting assistant, while the evaluation engine is
domain-independent.

## Stable v1.0 capabilities

- Load a versioned evaluation scenario from JSON.
- Score citations, groundedness, latency, and estimated cost.
- Run deterministic red-team checks for secret leakage and unsafe autonomy.
- Produce a JSON report and a release-gate decision.
- Expose the same workflow through Python, CLI, and an optional FastAPI app.
- Compare candidate responses against a baseline and block regressions.
- Export a PR-ready Markdown comparison report.
- Publish JSON Schemas for portable scenario and report contracts.
- Import portable JSONL traces and extend scoring through evaluator plugins.
- Save experiment history locally with SQLite.
- Run an optional API and browser workbench in a hardened container baseline.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,api]'
pytest
ragops evaluate \
  --scenario scenarios/japanese_troubleshooting/scenario.json \
  --responses scenarios/japanese_troubleshooting/sample_responses.json
ragops compare \
  --scenario scenarios/japanese_troubleshooting/scenario.json \
  --baseline scenarios/japanese_troubleshooting/sample_responses.json \
  --candidate scenarios/japanese_troubleshooting/regressed_responses.json \
  --format markdown
uvicorn apps.api.main:app --reload
```

## Repository map

```text
apps/api/                  Optional HTTP interface
src/ragops/                Evaluation and red-team engine
scenarios/                 Versioned datasets and policies
schemas/                   Portable JSON Schema contracts
tests/                     Contract and behavior tests
docs/product/              Product thesis and requirements
docs/project/              Scope, milestones, and acceptance
docs/architecture/         System design and ADRs
```

## Product principles

1. Evaluation is a release contract, not a dashboard decoration.
2. Deterministic checks run before model-based judges.
3. Every score is traceable to a case, evidence, and policy version.
4. Scenario data is portable; hosted services are optional.
5. The open-source core must remain useful without a commercial control plane.

See [Product thesis](docs/product/product_thesis.md),
[v0.1 requirements](docs/product/requirements-v0.1.md), and
[architecture](docs/architecture/system-overview.md).

Start with [Getting started](docs/getting-started.md). Release history is in
[CHANGELOG.md](CHANGELOG.md); security and contribution policies are documented
in [SECURITY.md](SECURITY.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
