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

Choose a second credential-free workflow with:

```bash
ragops demo --scenario support-triage --output support-triage-demo
```

For a presales workflow:

```bash
ragops demo --scenario proposal-review --output proposal-review-demo
```

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

Optional evaluators add diagnostic metrics without changing the core scenario
contract. For example:

```bash
ragops evaluate \
  --scenario scenarios/japanese_troubleshooting/scenario.json \
  --responses scenarios/japanese_troubleshooting/sample_responses.json \
  --evaluator answer_length_budget \
  --answer-length-limit 500
```

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
RAGOPS_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" \
  docker compose up --build
open http://localhost:8000
```

Compose requires `RAGOPS_API_KEY` and binds to `127.0.0.1:8000` by default.
Protected endpoints fail closed when no key is configured. For an explicitly
unauthenticated local process, set `RAGOPS_INSECURE_DEV_MODE=true`; never use
that mode on a shared host. Requests default to 2 MiB and evaluation collections
to 1,000 cases, configurable with `RAGOPS_MAX_REQUEST_BYTES` and
`RAGOPS_MAX_CASES`. Interactive API documentation is available at `/docs`.
