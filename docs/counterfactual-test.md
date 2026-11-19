# Counterfactual-evidence test

Grounding scores compare an answer with the evidence it was given. On long answers they are weak
(see the [RAGTruth case study](case-study-ragtruth.md)). This test asks a different question: **does
the answer depend on the evidence at all?** It alters the evidence and asks your own system again.

```bash
ragops counterfactual --scenario scenario.json --responses responses.json \
  --answer-command "python my_app_adapter.py"
```

`--answer-command` runs without a shell. It reads one JSON object on stdin and prints one on stdout:

```json
{"case_id": "refund", "question": "How many days ...?", "evidence": ["passage 1", "passage 2"]}
```
```json
{"answer": "Customers can request a refund within 30 days."}
```

Your adapter must answer **using only the evidence it is given** (call your generation step, not your
live retriever), otherwise the test measures your retriever instead.

## Perturbations

| Name | What changes | The answer is flagged when |
| --- | --- | --- |
| `remove_support` | Passages that support the baseline answer are removed | the new answer is still at least `--same-threshold` (default 0.8) similar by token Jaccard |
| `swap_number` | Numbers that the baseline answer took from the evidence (and that are not in the question) are replaced by different numbers | the new answer still states an old number |

A case is *eligible* for a perturbation only if it applies (the answer must have supporting passages, or
state a number from the evidence). The run is `BLOCK` (exit 2) when more than `--max-insensitive-rate`
(default 20%) of eligible cases ignore the change, `INCONCLUSIVE` (exit 3) when fewer than `--min-eligible`
(default 3) cases were eligible, and `PASS` (exit 0) otherwise. Use `--limit N` to cap how many cases are sent.

## What this does not tell you

- It needs your system: it makes up to two calls per case. Run it against a test environment; the command is
  yours, RAGOps adds no network access.
- Redundant evidence (two passages stating the same fact) can make a faithful answer look unchanged. Flagged
  cases are leads to read, not verdicts.
- A system that always abstains passes `remove_support` trivially; read the answers too.
- It cannot tell a wrong-but-evidence-based answer from a right one. It detects answers that **ignore** the
  evidence, not answers that misuse it.

## Demo on two toy systems (mechanics only)

`examples/counterfactual_demo/` holds a scenario, a toy extractive system that answers from the evidence and a
toy system that answers from memory. Result on 8 cases:

| System | `remove_support` ignored | `swap_number` ignored (6 eligible) | Decision |
| --- | ---: | ---: | --- |
| `faithful_app.py` (uses the evidence) | 0 / 8 | 0 / 6 | PASS |
| `memorizing_app.py` (ignores it) | 8 / 8 | 6 / 6 | BLOCK |

These are deliberately extreme toys. The result shows the test can separate the two behaviours; it is **not**
evidence about how well it works on a real RAG system, which has not been measured yet.
