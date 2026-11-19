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
