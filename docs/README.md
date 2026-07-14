# RAGOps documentation

Start with the path that matches the decision you need to make. Current guides
are separated from immutable release records so old planning language is not
mistaken for active product guidance.

## Adopt RAGOps

1. [Reach a release decision in five minutes](getting-started.md).
2. [Export your first portable trace](engineering/export-your-first-trace.md).
3. Add a [GitHub pull-request gate](engineering/github-pr-gate.md) or
   [GitLab merge-request gate](engineering/gitlab-ci-gate.md).
4. Promote [evaluator metrics and findings](evaluation/evaluator-gates.md) into
   reviewed release policy when needed.

## Understand the product

- [Product thesis](product/product_thesis.md)
- [System overview](architecture/system-overview.md)
- [System context](architecture/context-diagram.md)
- [Component architecture](architecture/component-diagram.md)
- [Evaluation strategy](evaluation/strategy.md)
- [Current roadmap](product/roadmap.md)
- [Known security limits](../SECURITY.md)

## Integrate evidence

- [Provider and external-metric adapters](engineering/provider-adapters.md)
- [OpenTelemetry example](../examples/opentelemetry_trace_adapter/README.md)
- [Observability contract](engineering/observability.md)
- [Safe pull-request comment publishing](architecture/pr-comment-publishing.md)
- [Local release verification](engineering/local-release.md)

## Reproduce the public evidence

- [Reference benchmark report](evaluation/benchmark-report-v0.2.md)
- [Japanese troubleshooting reference agent](../examples/japanese_troubleshooting_agent/README.md)
- [Five-minute demo walkthrough](demo/walkthrough.md)
- [Portfolio case study](demo/portfolio-case-study.md)
- [Presentation outline](demo/presentation-outline.md)

Synthetic fixtures demonstrate repeatability and release-gate behavior. They do
not prove semantic correctness, production security, customer adoption, or ROI.

## Immutable project records

The following folders are historical evidence, not current instructions:

- `architecture/adr/` — accepted architecture decisions.
- `product/requirements-v*.md` — released requirements and the current
  owner-review slice.
- `project/*acceptance.md` and `project/closure.md` — acceptance and closure
  records at the time they were written; the v2.4.1 candidate remains pending
  owner publication approval.
- `releases/` and the released sections of `../CHANGELOG.md` — published release
  notes.
- `design-audit/` — visual evidence referenced by historical acceptance records.

These records remain unchanged unless a correcting record explicitly
supersedes them. Their dates and status statements describe that historical
moment, not the current documentation refresh.
