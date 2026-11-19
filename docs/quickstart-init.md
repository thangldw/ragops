# First result on your own data: `ragops init`

```bash
ragops init --from path/to/logs --output ragops-gate
ragops evaluate --scenario ragops-gate/scenario.json \
  --responses ragops-gate/responses.json --evaluator strict_grounding --format markdown
```

`--from` takes a JSON or JSONL file, or a directory of them. Each record needs a
question, an answer and the retrieved contexts. Field names are inferred, for example
`question|query|prompt|input.question`, `answer|output|response`,
`contexts|retrieved_contexts|documents|retrieval.contexts` (strings or objects with
`text`/`content`/`page_content` and an `id`). Records that lack one are skipped and counted.

It writes `scenario.json`, `responses.json` and `first-report.md`, and runs a first
`strict_grounding` evaluation. It never overwrites existing files and refuses symlinks.

What the output means:
- Latency and cost limits come from your logs (p95 × 1.25, max × 1.25). Quality thresholds
  are conservative defaults. Tune them in `scenario.json`.
- `required_citation_ids` are the citations found in your logs. Review them.
- A failing first run usually points at unsupported answers already in your logs. Read
  `first-report.md` before loosening thresholds. Findings are leads, not verdicts.

## Importing from LLM platforms

```bash
ragops init --from langfuse-export.json --source-format langfuse --output gate
ragops init --from chat-logs.jsonl     --source-format openai    --output gate
ragops init --from messages-logs.jsonl --source-format anthropic --output gate
```

| Format | Question | Answer | Retrieved contexts | Other |
| --- | --- | --- | --- | --- |
| `langfuse` | trace `input` | trace `output` (else first generation) | `RETRIEVER` observations | `latency` (s), `totalCost` |
| `openai` | last `user` message | `choices[0].message.content` | `tool` messages and `<context>`/`<documents>` tags in the prompt | `latency_ms`, `cost_usd` if present |
| `anthropic` | last `user` message | text blocks of the response | `document`, `search_result` and `tool_result` blocks, `<context>` tags | citations, `latency_ms`, `cost_usd` if present |

Limits, stated plainly:
- OpenAI and Anthropic logs carry no retrieval by themselves. A record with no tool results,
  documents or tagged context is skipped and counted; nothing is guessed.
- Cost comes only from a `cost`/`totalCost` field. Token counts are never converted to money.
- These mappings follow the documented shapes of each platform's exports and are covered by
  fixture tests. They have not been run against a live account export. If yours differs,
  `--source-format generic` with the field aliases above is the fallback; please report the shape.
