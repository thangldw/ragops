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
