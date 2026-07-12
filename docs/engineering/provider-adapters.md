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

