# Five-minute demo walkthrough

**Audience:** an engineer who operates a RAG or agent system.

**Decision:** whether RAGOps can reproduce a reviewable release gate without a
provider account or model API.

## 0:00–1:00 — ask the release question

“We changed a prompt, retriever, embedding model, dataset, or evaluator. Is the
candidate still good enough to release?”

Clarify the boundary: RAGOps sits outside the application and evaluates recorded
behavior against a versioned contract.

## 1:00–2:00 — run the proof

```bash
pip install ragops==2.4.0
ragops demo --output ragops-demo
```

The command completes because it reproduced the expected experiment. A blocked
candidate is a valid release decision, not a process failure.

## 2:00–3:00 — compare PASS and BLOCK

Open `ragops-demo/release-report.html` and show:

- Baseline `PASS`: the accepted fixture meets the frozen policy.
- Candidate `BLOCK`: named metrics and cases exceed release tolerances.
- Portable evidence: scenario, fixtures, JSON, Markdown, and HTML.

## 3:00–4:00 — trace one finding

Follow one aggregate regression to its case, answer, citation, metric delta,
and policy rule. Keep the focus on evidence lineage rather than a single score.

## 4:00–5:00 — map to the adopter's stack

Replace demo responses with recorded application output or JSONL traces. Import
optional Ragas, DeepEval, Langfuse, or internal-judge metrics through the
portable envelope when those tools already exist.

Close with the evidence boundary: lexical overlap is not semantic entailment,
synthetic fixtures are not customer evidence, and the local alpha is not hosted
production infrastructure.
