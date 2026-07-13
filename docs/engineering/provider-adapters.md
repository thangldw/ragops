# Provider adapters

RAGOps core remains provider-neutral and dependency-free. Optional adapters may
generate application outputs, but evaluation consumes the same portable trace
contract regardless of provider.

## OpenAI Responses API

`OpenAIResponsesAdapter` sends an explicit model and input to
`POST /v1/responses`, extracts text output, and records response/model/token
metadata. The model has no default: production evaluations should pin a chosen
model or snapshot rather than silently following an alias.

The adapter follows the official Responses API/model guidance:
https://developers.openai.com/api/docs/models

```python
from ragops.providers import OpenAIResponsesAdapter

adapter = OpenAIResponsesAdapter(
    api_key=os.environ["OPENAI_API_KEY"],
    model=os.environ["RAGOPS_OPENAI_MODEL"],
)
result = adapter.generate(
    instructions="Answer only from approved evidence and cite sources.",
    input_text=question,
)
```

No live provider test runs in public CI. Tests inject a recorded transport so
contributors do not need credentials and secrets never enter fixtures.

## External evaluator metrics

RAGOps does not require teams to replace Ragas, DeepEval, Langfuse, or an
internal judge. Export their per-case numeric results into the versioned
`external-metrics-0.1` envelope:

```json
{
  "schema_version": "0.1",
  "provider": "ragas",
  "records": [
    {
      "case_id": "error-e42",
      "metrics": {"faithfulness": 0.96, "answer_relevance": 0.94}
    }
  ]
}
```

RAGOps preserves the supplied scale and meaning. It only validates coverage and
finite numeric values, namespaces the metrics, aggregates them, and applies the
reviewed release policy.

```bash
ragops evaluate \
  --scenario scenarios/japanese_troubleshooting/scenario.json \
  --responses scenarios/japanese_troubleshooting/sample_responses.json \
  --external-metrics scenarios/japanese_troubleshooting/external-metrics-baseline.json \
  --evaluation-policy scenarios/japanese_troubleshooting/external-metric-policy.toml

ragops compare \
  --scenario scenarios/japanese_troubleshooting/scenario.json \
  --baseline scenarios/japanese_troubleshooting/sample_responses.json \
  --candidate scenarios/japanese_troubleshooting/sample_responses.json \
  --baseline-external-metrics scenarios/japanese_troubleshooting/external-metrics-baseline.json \
  --candidate-external-metrics scenarios/japanese_troubleshooting/external-metrics-candidate.json \
  --evaluation-policy scenarios/japanese_troubleshooting/external-metric-policy.toml
```

The second command intentionally returns exit code 2 because candidate
faithfulness is below policy. Native framework export parsing stays outside the
dependency-free core so vendor upgrades cannot silently change the RAGOps
contract.
