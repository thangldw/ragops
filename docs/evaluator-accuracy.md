# Evaluator accuracy

RAGOps' default evaluators are deterministic and lexical. This page states how accurate they are, on what data, and where they fail.

## Benchmark

`benchmarks/grounding/` holds 61 evidence/answer pairs (English, Vietnamese, Japanese) labeled `1` (answer fully supported by the evidence) or `0`. The pairs were written and labeled by the maintainer to cover paraphrases, copies, subsets, wrong numbers, wrong identifiers, negation flips, role swaps, extra claims and unrelated answers. **They are not independent human annotation and are not production data.** `dev` (30) was used while developing `strict_grounding`; `heldout` (31) was written beforehand and not used for tuning.

Reproduce with `python scripts/grounding_benchmark.py`. `tests/test_grounding_benchmark.py` fails if strict grounding drops below 85% accuracy or stops beating the baseline by 10 points.

| Evaluator | Split | Accuracy | False-pass | False-block |
| --- | --- | ---: | ---: | ---: |
| `lexical_groundedness` (default, threshold tuned on dev) | dev | 57% | 39% | 50% |
| `lexical_groundedness` | heldout | 71% | 32% | 25% |
| `strict_grounding` (opt-in) | dev | 90% | 11% | 8% |
| `strict_grounding` | heldout | 87% | 5% | 25% |

## What `strict_grounding` adds

Enable with `ragops evaluate --evaluator strict_grounding`. Every claim must be supported by a single evidence sentence; numbers and one-character identifiers must match exactly; a negation mismatch is a `contradicted_claim`; extra clauses (`and ...`) must be supported separately. Japanese/Chinese use character bigrams and Vietnamese is NFC-normalized.

## Known failures

- Synonym paraphrases ("ship free within the country" vs "qualify for free domestic shipping") are false-blocked.
- Swapped words that keep the same vocabulary ("first day" vs "last day", "Admins can delete" vs "Members can delete") can be false-passed.
- Japanese paraphrase is weak because bigram overlap is coarse.

`lexical_groundedness` stays the default so existing scores and baselines do not move. For semantic grounding, import Ragas/DeepEval/LLM-judge scores through the adapters and measure them against your own human labels with `ragops calibrate`.
