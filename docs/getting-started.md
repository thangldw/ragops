# Getting started

## Generate the five-minute proof

```bash
ragops demo --output ragops-demo
```

This credential-free command writes a portable scenario, accepted baseline,
intentionally regressed candidate, Markdown report, and standalone HTML report.
The command succeeds when the expected candidate is blocked.
It refuses to reuse an existing output directory by default. Use `--force`
only when you intentionally want to replace regular demo files there.

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

For pull requests, use the
[reusable GitHub release gate](engineering/github-pr-gate.md) to preserve the
same exit decision while publishing a job summary and evidence artifact.

## Import application traces

Export one JSON object per line following
`schemas/trace-0.4.schema.json`, then load it with
`ragops.traces.load_trace_jsonl`. Provider-specific adapters should map their
events into this envelope instead of changing the core domain model.
See [Export your first portable trace](engineering/export-your-first-trace.md)
for a complete credential-free walkthrough.
If the application already exports OpenTelemetry spans, start with the
[dependency-free span adapter](../examples/opentelemetry_trace_adapter/README.md).

## Run the workbench

```bash
docker compose up --build
open http://localhost:8000
```

Set `RAGOPS_API_KEY` before exposing the service beyond localhost. Interactive
API documentation is available at `/docs`.
