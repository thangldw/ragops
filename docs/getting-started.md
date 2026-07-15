# Getting started

RAGOps evaluates a RAG or AI agent you already operate. It does not build the
retriever, generator, or orchestration layer.

## 1. Run the credential-free proof

```bash
python -m venv .venv
source .venv/bin/activate
pip install ragops==1.0.0
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

## 4. Compare repeated metric observations

Use the experimental statistical path when baseline and candidate bundles
contain multiple recorded metric observations per scenario case:

```bash
ragops compare-runs \
  --baseline-bundle scenarios/statistical_gate/baseline.json \
  --candidate-bundle scenarios/statistical_gate/candidate-pass.json \
  --policy scenarios/statistical_gate/policy.toml \
  --format markdown
```

This path gates both the absolute candidate confidence bound and the
uncertainty-aware baseline delta. It returns exit `2` for a measured regression,
an absolute failure, or insufficient distinct-case evidence.

Use predeclared sequential looks when additional repeats are expensive:

```bash
ragops compare-sequential \
  --baseline-bundle scenarios/statistical_gate/baseline.json \
  --candidate-bundle scenarios/statistical_gate/candidate-pass.json \
  --policy scenarios/statistical_gate/sequential-policy.toml
```

Before promoting a baseline, bind its exact bundle and policy bytes. Signing is
an explicit owner operation:

```bash
ragops baseline-create \
  --bundle baseline.bundle.json \
  --policy statistical-policy.toml \
  --owner thang \
  --accepted-at 2026-07-15T21:00:00+09:00 \
  --output baseline-manifest.json

ragops baseline-sign \
  --manifest baseline-manifest.json \
  --key path/to/ssh-signing-key \
  --output baseline-manifest.sig
```

`baseline-verify` always checks bundle and policy digests. Add the signature,
allowed-signers file, and identity arguments together to verify owner identity.

## 5. Integrate the gate

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
