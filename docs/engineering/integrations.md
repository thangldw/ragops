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

For repeated evaluation events,
`otel_evaluation_events_to_observations` maps `gen_ai.evaluation.name` and
`gen_ai.evaluation.score.value` plus `ragops.case.id` and
`ragops.repeat.id` into replay observations. The GenAI conventions are still
moving, so the replay evaluator provenance must record the convention and
adapter version. See the [OpenTelemetry GenAI attribute registry](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/).

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

For repeated statistical runs, dependency-free bridges accept recorded
provider structures:

- `ragas_scores_to_observations` maps ordered
  [`EvaluationResult.scores`](https://docs.ragas.io/en/latest/references/evaluation_schema/)
  rows to explicit case IDs and one repeat ID.
- `deepeval_scores_to_observations` maps recorded metric names and numeric
  [DeepEval `metric.score`](https://deepeval.com/docs/metrics-introduction)
  values while preserving repeat IDs.

These functions do not import provider packages. The application owns SDK
execution, score extraction, redaction, evaluator identity, prompt/model
provenance, and the mapping review.

## Repeated-run command adapter

A run plan declares bounded case IDs, repeat count, scenario digest, and full
provenance. The explicit command emits one JSON object per invocation:

```json
{"metrics":{"citation_precision":0.94}}
```

```bash
ragops collect-runs \
  --plan scenarios/statistical_gate/run-plan.json \
  --output candidate.bundle.json \
  --command -- python your_metric_runner.py
```

The command inherits the caller environment and receives case/repeat IDs in
environment variables. Do not pass untrusted commands or secrets into a pull
request job. Use `--resume` to continue an interrupted bundle. Add
`--baseline-bundle` and `--sequential-policy` to stop after a terminal complete
round.

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
