# 60-second adoption video script

## 0:00–0:10 — The change

Show a prompt/retriever/model change and ask: “Is this candidate still safe
enough and useful enough to release?”

## 0:10–0:22 — Install and run

```text
pip install ragops==2.4.0
ragops demo --output ragops-demo
```

Say: “No model API. No hosted dependency. Five minutes to reviewable evidence.”

## 0:22–0:38 — Decision

Open the report. Baseline is `PASS`; candidate is `BLOCK`. Highlight named
citation, groundedness, latency, or cost gates rather than an opaque score.

## 0:38–0:50 — Fit your stack

Show portable responses/traces and optional metrics from Ragas, DeepEval,
Langfuse, or an internal judge entering the same versioned policy.

## 0:50–1:00 — Honest close

“RAGOps evaluates the system you already have. Synthetic fixtures validate the
harness; your reviewed production evidence decides what ships.”
