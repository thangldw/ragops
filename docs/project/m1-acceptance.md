# M1 acceptance — benchmark credibility

## Decision

**Accepted for the synthetic benchmark milestone.** RAGOps now demonstrates a
repeatable pass/hold decision across quality, citations, operational budgets,
and deterministic policy findings. This acceptance does not claim production
model quality or external customer validation.

## Evidence

- Scenario 0.2 with backwards-compatible 0.1 loading.
- Thirty Japanese cases across nine published taxonomy families.
- Passing baseline plus explicit regressed and adversarial fixture overlays.
- Citation coverage, citation precision, lexical groundedness, latency, cost,
  and critical policy gates.
- Optional claim-support, citation-correctness, and retrieval-recall evaluators.
- Portable trace, attack-pack, scenario, response-fixture, and report contracts.
- Benchmark inspector, per-case HTML drill-down, reproducible benchmark report,
  automated tests, and CI expected-failure gates.

## Acceptance checks

- [x] Benchmark contains at least 30 cases.
- [x] Every taxonomy family contains at least three cases.
- [x] Baseline passes all absolute release gates.
- [x] Regressed candidate fails citation, quality, latency, and cost gates.
- [x] Adversarial candidate produces critical findings and is blocked.
- [x] Public contract extensions have schemas, ADRs, and compatibility tests.
- [x] Evaluator limitations are documented without semantic overclaiming.
- [x] Lint, tests, CLI workflows, and diff validation pass.

## Deferred to M2 and later

- A reference RAG/agent application producing traces from model execution.
- Human-labeled semantic entailment calibration and provider-backed judges.
- Executing attack packs against a target adapter.
- Customer-derived evaluation data and measured workflow impact.
- Hosted collaboration, production identity, and tenant isolation.

