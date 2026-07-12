# OpenTelemetry span-to-trace example

This dependency-free adapter turns already-exported, filtered OpenTelemetry
span JSONL into the portable RAGOps trace 0.4 envelope. It is an integration
example, not an SDK, collector, or change to core evaluation semantics.

## Run it

From the repository root:

```bash
PYTHONPATH=src python -m examples.opentelemetry_trace_adapter.adapter \
  --input examples/opentelemetry_trace_adapter/spans.jsonl \
  --output /tmp/ragops-otel-traces.jsonl

ragops evaluate \
  --scenario scenarios/japanese_troubleshooting/scenario.json \
  --traces /tmp/ragops-otel-traces.jsonl \
  --evaluator citation_correctness \
  --evaluator claim_support \
  --format markdown \
  --output /tmp/ragops-otel-report.md
```

The included synthetic spans produce two evaluable traces and require no
provider credentials.

## Attribute mapping

| Span field or attribute | Trace 0.4 field | Required |
| --- | --- | --- |
| `ragops.case_id` | `case_id` | Yes |
| `gen_ai.prompt` | `input.question` | Yes |
| `gen_ai.response.text` | `output.answer` | Yes |
| `ragops.citation_ids` | `output.citation_ids` | No |
| `ragops.retrieved_document_ids` | `retrieval.document_ids` | No |
| span timestamps or `duration_ms` | `latency_ms` | Yes |
| `ragops.cost_usd` | `usage.cost_usd` | No |
| `service.name`, `service.version` | trace metadata | No |

Applications should export only the attributes required for evaluation. Remove
secrets, personal data, unneeded prompt content, and sensitive document text
before writing fixtures or uploading report artifacts.
