# RAGOps portfolio case study

## From AI change to defensible release decision

RAG and agent teams can ship a prompt, retriever, embedding, or dataset change
quickly. The harder problem is deciding whether the candidate is still good
enough to release. Quality scores, operational budgets, citations, and review
notes often live in separate tools with no accepted baseline.

I built RAGOps as the provider-independent evidence layer between an AI change
and a release. It consumes recorded responses, portable traces, and optional
external evaluator metrics; applies versioned absolute and regression policy;
then emits an explainable `PASS` or `BLOCK` decision in JSON, Markdown, or HTML.

## Five-minute proof

```bash
pip install ragops==2.4.0
ragops demo --output ragops-demo
```

The generated report shows an accepted baseline passing and an intentionally
regressed candidate blocked with named reasons. No model API is required.

## Evidence

- Dependency-free Python 3.11+ evaluation core.
- 30-case synthetic release-gate fixture across nine failure families.
- Graph+ACL reference agent whose lexical-only candidate records 25-point
  citation coverage and precision regressions.
- Portable Ragas, DeepEval, Langfuse, and internal-judge metric envelope.
- Build-once GitHub/PyPI releases with byte-identical artifacts, SBOM, and
  checksums; v2.4.0 release validation passed 144 tests.

## Product boundary

RAGOps evaluates an existing RAG or agent. It does not replace orchestration,
retrieval, generation, model observability, or human review. Synthetic evidence
validates the harness, not semantic correctness, production security, customer
adoption, or ROI.

## Current recommendation

Use v2.4.0 for offline evaluation and customer discovery. Convert real failures
into reviewed regression fixtures before expanding into hosted collaboration.
