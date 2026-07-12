# Export your first portable trace

This tutorial turns two synthetic application events into RAGOps release
evidence without a model API, telemetry backend, or provider SDK.

## 1. Install the released CLI

Download the wheel from the
[v1.7.0 GitHub Release](https://github.com/thangldw/ragops/releases/tag/v1.7.0),
then install it:

```bash
python -m venv .venv
source .venv/bin/activate
pip install ./ragops-1.7.0-py3-none-any.whl
```

For repository development, `pip install -e .` is equivalent.

## 2. Export one JSON object per evaluated task

Each line needs a case ID, answer, latency, and optional citations, retrievals,
cost, approval state, and metadata:

```json
{"schema_version":"0.4","case_id":"error-e42","input":{"question":"A1000 E-42 first response?"},"output":{"answer":"Stop A1000, inspect the cooling fan guard, remove debris, then restart below 60C.","citation_ids":["manual-a1000-e42"]},"retrieval":{"document_ids":["manual-a1000-e42","incident-e42-2025"]},"latency_ms":1250,"usage":{"cost_usd":0.012},"metadata":{"application":"support-agent","build":"pr-42","retriever":"hybrid"}}
```

Write one line for every case in the selected scenario. The repository includes
a complete credential-free example at
`scenarios/japanese_troubleshooting/sample_traces.jsonl`.

## 3. Evaluate the trace

```bash
ragops evaluate \
  --scenario scenarios/japanese_troubleshooting/scenario.json \
  --traces scenarios/japanese_troubleshooting/sample_traces.jsonl \
  --evaluator citation_correctness \
  --evaluator claim_support \
  --format markdown \
  --output /tmp/ragops-trace-report.md
```

Exit `0` means the recorded build meets the scenario contract. Exit `2` means
evaluation completed but at least one release gate blocked the build.

## 4. Integrate without changing the core

Map framework/provider events into the portable envelope in an adapter owned by
the application. Keep raw prompts, secrets, personal data, and unnecessary
document content out of public fixtures. RAGOps reports can contain answers and
evidence, so apply the same access and retention policy as the source traces.

Next: use the [reusable GitHub PR gate](github-pr-gate.md) to compare an accepted
baseline with every candidate build.
