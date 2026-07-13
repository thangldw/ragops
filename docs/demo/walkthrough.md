# Five-minute demo walkthrough

Audience: an engineer who already operates a RAG or agent system and needs a
repeatable release decision.

## Minute 0–1: state the release question

“The system already works. We changed a prompt, retriever, embedding model, or
dataset. Is the candidate still good enough to release?”

RAGOps sits outside the application. It consumes recorded evidence and applies
the same versioned policy to baseline and candidate.

## Minute 1–2: run the proof

```bash
pip install ragops==2.4.0
ragops demo --output ragops-demo
```

Explain that process success and release decision are separate: the command
returns successfully because it reproduced the expected blocked regression.

## Minute 2–3: inspect PASS and BLOCK

Open `ragops-demo/release-report.html`.

- Baseline: `PASS`, because it satisfies the frozen scenario and thresholds.
- Candidate: `BLOCK`, with named metric and case-level reasons.
- Evidence: portable JSON, Markdown, HTML, scenario, baseline, and candidate.

## Minute 3–4: trace one failure

Follow one aggregate regression to its case, answer, citations, metric delta,
and policy rule. Emphasize evidence lineage rather than a single dashboard score.

## Minute 4–5: map to the adopter's stack

Replace the demo responses with recorded application output or JSONL traces.
Keep model, retriever, and orchestration choices outside RAGOps. Import optional
Ragas, DeepEval, Langfuse, or internal-judge metrics through the portable metric
envelope when those tools already exist.

Close honestly: lexical groundedness is not semantic entailment, synthetic
fixtures are not customer evidence, and the local control plane is not hosted
production infrastructure.
