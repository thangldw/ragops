# RAGOps portfolio case study

## Decision enabled

Help an engineering team decide whether a changed RAG or AI-agent candidate is
still good enough to release.

## Problem

Prompt, retriever, embedding, dataset, and evaluator changes can preserve fluent
answers while degrading citations, evidence support, latency, cost, or safety.
Isolated dashboard scores do not identify the accepted baseline or explain why
a release should continue or stop.

## Product thesis

RAGOps is a provider-independent regression release gate for systems teams
already operate. It consumes recorded responses, portable traces, and optional
external evaluator metrics; applies versioned absolute and regression policy;
then emits an explainable `PASS` or `BLOCK` in JSON, Markdown, or HTML.

## Reproducible proof

```bash
pip install ragops==2.4.0
ragops demo --output ragops-demo
```

The generated report shows an accepted baseline passing and an intentionally
regressed candidate blocked with named reasons. No model API is required.

## Recorded evidence

- Dependency-free Python 3.11+ evaluation core.
- Thirty-case synthetic benchmark across nine failure families.
- Graph+ACL reference agent whose lexical-only candidate records 25-point
  citation coverage and precision regressions.
- Portable metric envelope for Ragas, DeepEval, Langfuse, and internal judges.
- Build-once release artifacts with checksums, SBOM, and clean-install evidence.

## Architecture boundary

RAGOps evaluates an existing system. It does not replace orchestration,
retrieval, generation, observability, or human approval. Optional APIs,
providers, and collaboration surfaces remain outside the dependency-free core.

## Limitations

Synthetic evidence validates harness behavior, not semantic correctness,
production security, customer adoption, or ROI. The reference ACL and local
control-plane alpha are development fixtures, not production identity or
multi-tenant infrastructure.

## Current recommendation

Use stable `2.4.0` for offline evaluation and discovery. Convert real failures
into reviewed regression fixtures before expanding policy or hosted surfaces.
