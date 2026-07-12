# Requirements v1.6 — pull-request adoption path

## User story

As an AI engineer evaluating RAGOps, I want a copyable pull-request gate,
printable evidence, and a minimal trace-export tutorial so that I can integrate
the project into an existing repository without learning its internal modules.

## Public contract impact

- Add a reusable GitHub Actions workflow under `.github/workflows/`.
- Add print presentation rules to the standalone comparison HTML report.
- Add documentation for exporting and evaluating portable traces.
- Do not change scenario, trace, report, evaluator, metric, CLI, API, or
  release-decision semantics.

## Acceptance criteria

1. A caller repository can invoke the reusable workflow with scenario,
   baseline, and candidate paths.
2. PASS returns a successful job; BLOCK and contract errors fail only after the
   Markdown evidence and command log are added to the Step Summary and artifact.
3. Workflow inputs reach shell commands through quoted environment variables,
   not direct expression interpolation.
4. Standalone HTML comparison reports have legible print rules and preserve
   decision, metric, gate, and case-detail content.
5. The trace tutorial runs against synthetic repository fixtures without a
   provider credential.
6. Tests verify workflow structure, documentation links, and print CSS.
7. A dependency-free OpenTelemetry example maps synthetic spans into valid
   trace 0.4 JSONL without changing the core trace loader or schema.

## Non-goals

- Posting write-enabled PR comments from forked pull requests.
- Publishing a new evaluator or changing metric meaning.
- Publishing to PyPI before Trusted Publisher ownership is configured.
- Claiming design-partner adoption or production ROI.
- Shipping an OpenTelemetry SDK, collector, or telemetry backend integration.
