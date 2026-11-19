# Case study: grounding evaluators on HaluEval QA (public data)

Our own benchmark (`docs/evaluator-accuracy.md`) was written and labeled by the maintainer, so it
cannot show how the evaluators behave on data they were not built around. This page does that
check on a public benchmark, with the protocol fixed before running.

## Data

[HaluEval](https://github.com/RUCAIBox/HaluEval) QA (MIT licence): 10,000 questions, each with
the supporting `knowledge`, a `right_answer` and a `hallucinated_answer`. File
`data/qa_data.json`, sha256 `89ed139ec5e3a3169a0b30e45569ac1283846f76f27f7bb5e908ee6deed57e88`.
Every pair gives two items: the right answer (should pass) and the hallucinated one (should block).
The data is not copied into this repository.

## Protocol

Zero-shot. No threshold was tuned on this data: `lexical_groundedness` uses the threshold chosen on
our own dev split (it came out at 1.0, exact containment) and `strict_grounding` uses 1.0.
Reproduce: `python scripts/public_benchmark.py qa_data.json`.

## Results (10,000 pairs, 20,000 judgements)

| Evaluator | Accuracy | Hallucination passed (false pass) | Right answer blocked (false block) |
| --- | ---: | ---: | ---: |
| `lexical_groundedness` | 92.9% | 7.6% (CI 7.1–8.1) | 6.6% (CI 6.1–7.1) |
| `strict_grounding` | 91.0% | 9.8% (CI 9.2–10.4) | 8.2% (CI 7.7–8.7) |

CI is the 95% Wilson interval for each rate.

## What this shows

- **The advantage on our own benchmark did not reproduce.** There strict beats lexical 93% to 72%;
  here lexical is slightly ahead (92.9% vs 91.0%). The own-benchmark gap was partly an artifact of
  who wrote the data, as `docs/evaluator-accuracy.md` already warned. Do not quote 93% as a
  general accuracy figure.
- **This dataset favours containment.** 95.5% of right answers are bare spans copied from the
  knowledge (about 2 words), while hallucinated answers are full sentences (about 11 words) that
  almost never appear verbatim (0.5%). An exact-containment check gets most of the signal from that
  length and form difference alone. It is not the sentence-form answer a RAG system usually gives.
- **Strict false blocks (819 of 10,000)** are mostly answers that need reasoning, not wording:
  "yes", "no", "director", "nine" against a passage that implies them.
- **Strict false passes (976)** are relational swaps that reuse the passage's own words:
  "Brooks Garth" for "Garth Brooks", "Neil Gaiman directed Beowulf" when the director is someone
  else, "Stanford University has a Chestnut Hill campus". A word-level check cannot see these.
  Neither can lexical grounding. Both need a semantic or entailment judge.

## Where the errors come from (strict_grounding)

Of 827 right answers blocked, 620 (75%) are bare `yes`/`no`; 205 are other short answers present in the passage. Of 967 hallucinations passed, 847 (88%) reuse the passage's own words in a wrong relation. Adding number-word normalisation (`nine` = `9`) and a reversed-name check (`Brooks Garth`) left accuracy unchanged at 91.0%: these rules are correct and tested, but they do not touch the dominant errors. Word matching has reached its ceiling here; the rest needs entailment (a semantic scorer).

## Takeaways

1. Neither lexical evaluator is a hallucination detector for short-form QA. About 8–10% of
   hallucinations pass, and 7–8% of right answers are blocked.
2. Use `strict_grounding` for what it does well (exact numbers, identifiers, negation, unsupported
   extra claims in sentence-form answers) and add a semantic scorer
   (`--evaluator semantic_grounding`, `docs/semantic-evaluator.md`) calibrated on your own labels
   for the rest.
3. Treat any single accuracy figure as specific to its dataset. Calibrate on your own data with
   `ragops calibrate` before gating a release on it.
