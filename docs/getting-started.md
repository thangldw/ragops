# Getting started: reach a release decision in five minutes

RAGOps evaluates an existing RAG or agent system. It does not build retrieval,
generation, or orchestration. Start with the credential-free proof, then replace
the fixtures with outputs from your application.

## 1. Install the stable CLI

```bash
python -m venv .venv
source .venv/bin/activate
pip install ragops==2.4.0
ragops --version
```

Expected version: `ragops 2.4.0`.

## 2. Generate the five-minute proof

```bash
ragops demo --output ragops-demo
open ragops-demo/release-report.html
```

The demo succeeds by reproducing an expected decision: the accepted baseline
passes and the intentionally regressed candidate is blocked. The directory
contains the scenario, response fixtures, JSON, Markdown, and standalone HTML
evidence. It requires no model API or external service.

Try the other included workflows:

```bash
ragops demo --scenario support-triage --output support-triage-demo
ragops demo --scenario proposal-review --output proposal-review-demo
```

## 3. Evaluate your recorded output

```bash
ragops evaluate \
  --scenario path/to/scenario.json \
  --responses path/to/responses.json \
  --format markdown \
  --output evaluation.md
```

Use `--traces` instead of `--responses` when your application exports portable
JSONL trace 0.4 records. See [export your first trace](engineering/export-your-first-trace.md).

## 4. Compare candidate with baseline

```bash
ragops compare \
  --scenario path/to/scenario.json \
  --baseline path/to/baseline.json \
  --candidate path/to/candidate.json \
  --evaluation-policy path/to/evaluation-policy.toml \
  --format html \
  --output release-report.html
```

- Exit `0`: evaluation completed and the candidate passes.
- Exit `2`: evaluation completed and policy blocks the candidate.
- Other non-zero exit: fixture, configuration, or contract error.

RAGOps can also gate namespaced per-case scores exported by Ragas, DeepEval,
Langfuse, or an internal judge. Imported metric meaning remains owned by the
producer and your reviewed policy.

## 5. Add the gate to team workflow

- [GitHub pull-request gate](engineering/github-pr-gate.md)
- [GitLab merge-request gate](engineering/gitlab-ci-gate.md)
- [Evaluator and finding policy](evaluation/evaluator-gates.md)
- [Provider-neutral metric adapter](engineering/provider-adapters.md)

## Optional local workbench

```bash
RAGOPS_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" \
  docker compose up --build
open http://localhost:8000
```

Compose binds to localhost and requires a key. The browser workbench is a local
adapter; evaluation semantics remain in the dependency-free core.

## What this proof does not establish

Synthetic fixtures validate the harness and release workflow. They do not prove
semantic correctness, production security, customer adoption, or ROI. Replace
them with reviewed, consented evidence from your own workflow before making
production claims.
