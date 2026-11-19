# Evaluator accuracy

RAGOps' default evaluators are deterministic and lexical. This page states how accurate they are, on what data, and where they fail.

## Benchmark

`benchmarks/grounding/` holds 97 evidence/answer pairs (English, Vietnamese, Japanese) in four splits, labeled `1` (answer fully supported by the evidence) or `0`. The pairs were written and labeled by the maintainer to cover paraphrases, copies, subsets, wrong numbers, wrong identifiers, negation flips, antonyms, role swaps, extra claims and unrelated answers. **They are not independent human annotation and are not production data.**

How each split was used: `dev` (30) was used while developing `strict_grounding`. `heldout` (31) was written beforehand and not used for tuning. `heldout2` (20) was written before the antonym and proper-noun checks but then used to develop them, so treat it as development data. `heldout3` (16) was written before those checks and not used for tuning, though the author knew which checks were coming, so it still flatters the result.

Reproduce with `python scripts/grounding_benchmark.py`. `tests/test_grounding_benchmark.py` fails if strict grounding drops below 85% accuracy on any split or stops beating the baseline by 10 points overall.

| Evaluator | dev | heldout | heldout2 | heldout3 | All 97 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `lexical_groundedness` (default, threshold tuned on dev) | 57% | 71% | 95% | 75% | 72% |
| `strict_grounding` (opt-in) | 90% | 90% | 100% | 94% | 93% |

Across all 97 pairs, lexical groundedness has 26% false-pass and 31% false-block; `strict_grounding` has 2% false-pass and 17% false-block. Lexical does well on `heldout2` only because that split is mostly one-word substitutions, which an exact-containment threshold catches while still rejecting every paraphrase.

## What `strict_grounding` adds

Enable with `ragops evaluate --evaluator strict_grounding`. Every claim must be supported by a single evidence sentence; numbers and one-character identifiers must match exactly; a negation mismatch, or an antonym pair (before/after, enabled/disabled, daily/weekly, 前/後, 有効/無効 and similar) between claim and evidence, is a `contradicted_claim`; capitalized proper nouns must also match; extra clauses (`and ...`) must be supported separately. Japanese/Chinese use character bigrams and Vietnamese is NFC-normalized.

## Known failures

- Synonym paraphrases ("ship free within the country" vs "qualify for free domestic shipping") are false-blocked.
- Role or word swaps with no entry in the antonym table ("Admins can delete" vs "Members can delete") can be false-passed; the antonym table is small and hand-written.
- Japanese paraphrase is weak because bigram overlap is coarse.

`lexical_groundedness` stays the default so existing scores and baselines do not move. For semantic grounding, import Ragas/DeepEval/LLM-judge scores through the adapters and measure them against your own human labels with `ragops calibrate`.

## Independent labels

The labels above are the maintainer's. To replace them with independent evidence, give each reviewer a blind sheet and ingest the results:

```bash
python scripts/grounding_labels.py export --reviewer alice --out alice.json   # no labels, no failure kinds
# reviewer sets "label" to 0 or 1 for every item and returns the file
python scripts/grounding_labels.py ingest --sheet alice.json --sheet bob.json \
    --evaluator strict --calibration-out calibration.json
ragops calibrate --input calibration.json
```

`ingest` validates every sheet, prints reviewer agreement (Cohen kappa) and each item where reviewers disagree with the maintainer, and writes a calibration set so `ragops calibrate` reports accuracy and false-pass/false-block rates against the human labels. No independent labels have been collected yet.
