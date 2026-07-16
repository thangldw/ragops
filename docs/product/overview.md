# Product overview

## Problem

RAG and AI-agent changes can preserve fluent output while degrading citations,
evidence support, latency, cost, or safety. Teams need a repeatable answer to:
**is this candidate still good enough to release?**

## Product thesis

RAGOps is a local-first regression release gate for teams that already operate
RAG or AI-agent systems. It evaluates recorded responses, portable traces,
repeated metric observations, and optional external metrics against versioned
scenarios and policies, then returns an explainable
`PASS` or `BLOCK` with case-level evidence.

## Users and jobs

| User | Decision enabled |
| --- | --- |
| AI engineer | Verify a prompt, retriever, embedding, dataset, or evaluator change |
| Engineering lead | Review and enforce an accepted release contract |
| Forward-deployed engineer | Turn pilot expectations into portable scenarios and evidence |
| Security or governance reviewer | Inspect critical findings and approval boundaries |

Priority workflows are pull-request gates, pilot acceptance, incident
regression fixtures, evaluator integration, and portable governance evidence.

## Product boundary

RAGOps owns scenarios, loaders, evaluators, findings, comparison, release gates,
and portable reports. It does not own retrieval, generation, orchestration,
identity, business actions, or production hosting.

The dependency-free core remains useful without an account or service. Optional
APIs, provider adapters, CI publishers, and local collaboration surfaces stay
outside evaluation semantics.

## Differentiation hypothesis

- Versioned, portable release contracts rather than isolated dashboard scores.
- Absolute readiness and baseline regression gates in one decision.
- Effect size plus uncertainty for stochastic systems, with valid predeclared
  sequential stopping.
- Provenance isolation for model, evaluator, dataset, and infrastructure
  changes, plus content-addressed accepted baselines.
- Deterministic evidence visible before optional model-based judgments.
- Offline execution with provider-neutral adapter boundaries.
- Critical policy findings that cannot be averaged away.

This positioning is a product hypothesis, not a claim that other products lack
these capabilities.

## Why this instead of X?

Choose the tool around the job you need most. This table reflects the linked
official documentation reviewed on 2026-07-16; products evolve, and RAGOps can
consume recorded scores from other evaluators rather than replace them.

| Tool | Strongest fit | What RAGOps adds when used beside it |
| --- | --- | --- |
| [Ragas](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/) | A broad library of RAG and agent metrics, experiments, and test-data generation | An offline release contract over recorded Ragas scores, with accepted-baseline integrity, critical non-compensating gates, and standalone evidence |
| [DeepEval](https://deepeval.com/docs/evaluation-unit-testing-in-ci-cd) | Pytest-native LLM evaluation and CI assertions, with optional hosted reports | Provider-neutral recorded-evidence replay, uncertainty-aware repeated-run comparison, and a bounded PR publication path |
| [Phoenix](https://arize.com/docs/phoenix) | OpenTelemetry tracing, evaluator debugging, datasets, experiments, and a visual workbench | A small dependency-free decision core that can gate exported evidence without running an observability service |
| [LangSmith](https://docs.langchain.com/langsmith/evaluation) | Managed offline/online evaluation, traces, datasets, human review, and experiment comparison | A fully local PASS/BLOCK artifact and versioned portable contracts that do not require a workspace |
| **RAGOps** | Reviewable release decisions from already-recorded evidence | It is intentionally not a tracing platform, model runner, hosted collaboration product, or large judge-metric library |

Use Ragas or DeepEval when evaluator breadth is the main need. Use Phoenix or
LangSmith when tracing, exploration, annotation, and a shared UI are central.
Use RAGOps when the final release decision must be reproducible offline and
auditable as repository evidence. Combining them is a supported path, not a
compromise.

## Success evidence

Repository evidence includes deterministic fixtures, reproducible PASS/BLOCK
decisions, schema validation, supported-version CI, package integrity, and
reviewable reports. Product outcomes require real measurements of activation,
repeat use, task success, time saved, critical incidents, and cost.

Targets and synthetic pilot results must never be presented as observed
customer adoption or ROI.

## Commercial boundary

Potential paid value may come from managed workspaces, identity, retention,
connectors, governance, operations, and enterprise support. A complete local
release-decision loop remains open source under MIT.
