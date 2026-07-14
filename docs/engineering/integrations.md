# Evidence and provider integrations

## Portable trace export

Write one trace 0.4 JSON object per evaluated task. Required evidence includes a
case ID, answer, and latency; citations, retrievals, cost, approval state, and
version metadata are optional but recommended.

```json
{"schema_version":"0.4","case_id":"error-e42","input":{"question":"A1000 E-42 first response?"},"output":{"answer":"Stop A1000 and inspect the cooling fan guard.","citation_ids":["manual-a1000-e42"]},"retrieval":{"document_ids":["manual-a1000-e42"]},"latency_ms":1250,"usage":{"cost_usd":0.012},"metadata":{"application":"support-agent","build":"pr-42","retriever":"hybrid"}}
```

```bash
ragops evaluate \
  --scenario scenarios/japanese_troubleshooting/scenario.json \
  --traces scenarios/japanese_troubleshooting/sample_traces.jsonl \
  --evaluator citation_correctness \
  --evaluator claim_support
```

Applications own redaction, allow-lists, retention, and mapping from framework
events into the portable envelope.

## OpenTelemetry

The dependency-free example under
[`examples/opentelemetry_trace_adapter/`](../../examples/opentelemetry_trace_adapter/README.md)
maps already-exported spans into trace 0.4 JSONL. It does not initialize an SDK,
contact a collector, or add OpenTelemetry to the core.

## External evaluator metrics

Export finite per-case scores from Ragas, DeepEval, Langfuse, or an internal
judge into the `external-metrics-0.1` envelope:

```json
{
  "schema_version": "0.1",
  "provider": "ragas",
  "records": [
    {"case_id": "error-e42", "metrics": {"faithfulness": 0.96}}
  ]
}
```

RAGOps validates coverage, namespaces aggregate keys as
`<provider>.<metric>`, and applies the reviewed policy. It does not reinterpret
direction, scale, calibration, or meaning.

## OpenAI Responses adapter

`OpenAIResponsesAdapter` is optional and requires an explicit model:

```python
from ragops.providers import OpenAIResponsesAdapter

adapter = OpenAIResponsesAdapter(api_key=api_key, model=model)
result = adapter.generate(
    instructions="Answer only from approved evidence and cite sources.",
    input_text=question,
)
```

Public tests inject a recorded transport. Live credentials and customer data
must never enter repository fixtures.

## Observability boundary

Portable metadata should record application build, prompt, retriever, index,
dataset, generator, role, token usage, and tool/approval outcomes when available.
Provider-specific spans remain application telemetry; the release contract uses
the stable portable evidence extracted from them.
