# Ten-minute presentation outline

## 1. Release question — 60 seconds

“We changed the RAG system. Is the candidate still good enough to release?”
Show why isolated scores and manual review do not create a defensible baseline.

## 2. Product thesis — 60 seconds

RAGOps is a provider-independent release-policy and evidence layer for existing
RAG and agents—not another orchestration framework.

## 3. Five-minute path — 90 seconds

Show install → demo → PASS baseline → BLOCK candidate → portable report.

## 4. Live evidence — 180 seconds

Run `ragops demo`, open the HTML report, and trace one aggregate regression to
its case, citations, metric delta, and versioned policy rule.

## 5. Extensibility — 90 seconds

Map portable responses/traces and Ragas, DeepEval, Langfuse, or internal scores
into the same gate. Keep provider semantics outside the dependency-free core.

## 6. Trust boundary — 90 seconds

Separate recorded synthetic evidence from production claims. Explain local-first
execution, exact artifact promotion, known limits, and why hosted 3.0 requires
real customer demand and operations.

## 7. Close — 30 seconds

“Evaluate with evidence. Release with a reason.”
