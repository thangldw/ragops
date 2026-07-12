# Getting started

## Evaluate one build

```bash
ragops evaluate \
  --scenario scenarios/japanese_troubleshooting/scenario.json \
  --responses scenarios/japanese_troubleshooting/sample_responses.json
```

## Guard a pull request against regressions

```bash
ragops compare \
  --scenario scenarios/japanese_troubleshooting/scenario.json \
  --baseline scenarios/japanese_troubleshooting/sample_responses.json \
  --candidate path/to/candidate-responses.json \
  --policy ragops.toml \
  --format markdown \
  --output reports/regression.md
```

Exit code `0` means release gates pass. Exit code `2` means evaluation completed
but the build is blocked. Invalid contracts exit non-zero with an explanation.

## Import application traces

Export one JSON object per line following
`schemas/trace-0.3.schema.json`, then load it with
`ragops.traces.load_trace_jsonl`. Provider-specific adapters should map their
events into this envelope instead of changing the core domain model.

## Run the workbench

```bash
docker compose up --build
open http://localhost:8000
```

Set `RAGOPS_API_KEY` before exposing the service beyond localhost. Interactive
API documentation is available at `/docs`.

