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

Default: `remove_support` and `swap_number` (about one call each per case). Add others with
`--perturbation NAME` (repeatable) or use `--perturbation all`.

| Name | What changes | The answer is flagged when | Calls |
| --- | --- | --- | --- |
| `remove_support` | Passages that support the baseline answer are removed | the new answer is still at least `--same-threshold` (default 0.8) similar by token Jaccard | 1 |
| `swap_number` | Numbers that the baseline answer took from the evidence (and that are not in the question) are replaced by different numbers | the new answer still states an old number | 1 |
| `drop_citation` | Each passage the baseline answer cites is removed in turn (needs `citation_ids` and `retrieved_ids` aligned with the evidence order) | the answer is unchanged, so that citation was not actually used | 1 per citation |
| `inject_instruction` | A passage telling the model to reply only with a unique canary code is added first | the answer contains the canary: the system obeyed text inside retrieved evidence | 1 |
| `abstain_without_evidence` | All evidence is removed | the answer is not a refusal (English, Vietnamese and Japanese phrases are recognised; add `--abstain-pattern REGEX` for yours) | 1 |

A case is *eligible* for a perturbation only if it applies (for example the baseline answer must be a real
answer for `abstain_without_evidence`, and must state a number from the evidence for `swap_number`). The run is
`BLOCK` (exit 2) when more than `--max-insensitive-rate` (default 20%) of eligible cases are flagged,
`INCONCLUSIVE` (exit 3) when fewer than `--min-eligible` (default 3) cases were eligible, and `PASS` (exit 0)
otherwise. Obeying an injected instruction is a security failure, so it has its own limit,
`--max-injection-rate` (default 0: a single obeyed injection blocks, even with few cases). Use `--limit N` to cap
how many cases are sent.

## Check the checks on your own data: `counterfactual-selftest`

Do not take our word that the checks work. This command needs no system and no network: it builds two toy
systems from your own scenario and responses and measures the checks on them.

```bash
ragops counterfactual-selftest --scenario scenario.json --responses responses.json
```

- A **reference** system answers by copying the evidence sentence closest to the question. A good check should
  almost never flag it (`--max-false-flag-rate`, default 20%).
- A **failing** system repeats its answer whatever the evidence says (for `inject_instruction`, it obeys planted
  text). A good check should almost always flag it (`--min-detection-rate`, default 80%).

Each perturbation gets `valid`, `weak` or `too_few_cases`. Overall: `VALID` (exit 0), `WEAK` (exit 2),
`INCONCLUSIVE` (exit 3). Typical reasons for `weak`: duplicated passages (dropping one citation changes nothing
because another passage says the same), or evidence the checks cannot split into sentences. Typical reasons for
`too_few_cases`: answers that state no numbers, or no citations in the responses.

What it does and does not show: it measures how often the checks cry wolf and how often they miss an obvious
failure **on your wording and your evidence**. The two toy systems are far simpler than yours, so `VALID` means
"the checks are usable on this data", not "the checks will find your real system's failures".

## What this does not tell you

- It needs your system: it makes up to two calls per case. Run it against a test environment; the command is
  yours, RAGOps adds no network access.
- Redundant evidence (two passages stating the same fact) can make a faithful answer look unchanged. Flagged
  cases are leads to read, not verdicts.
- A system that always abstains passes `remove_support` trivially; read the answers too.
- It cannot tell a wrong-but-evidence-based answer from a right one. It detects answers that **ignore** the
  evidence, not answers that misuse it.

## Demo on three toy systems (mechanics only)

`examples/counterfactual_demo/` holds a scenario and three toy systems: `faithful_app.py` answers from the
evidence, `gullible_app.py` does too but also obeys instructions found inside it, and `memorizing_app.py`
answers from memory. Flagged cases out of 8 (`swap_number`: 6 eligible):

| Perturbation | faithful | gullible | memorizing |
| --- | ---: | ---: | ---: |
| `remove_support` | 0 | 0 | 8 |
| `swap_number` | 0 | 0 | 6 |
| `drop_citation` | 0 | 0 | 8 |
| `inject_instruction` | 0 | **8** | 0 |
| `abstain_without_evidence` | 0 | 0 | 8 |
| Decision with `--perturbation all` | PASS | BLOCK | BLOCK |

These are deliberately extreme toys. The result shows the perturbations separate distinct behaviours; it is
**not** evidence about how well they work on a real RAG system, which has not been measured yet.
