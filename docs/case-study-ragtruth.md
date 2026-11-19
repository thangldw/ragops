# Case study: grounding evaluators on RAGTruth (public data, long answers)

[RAGTruth](https://github.com/ParticleMedia/RAGTruth) holds LLM responses to RAG prompts with
human-annotated hallucination spans. A response counts as hallucinated here when it has at
least one annotated span. We use the QA and Summary tasks (Data2txt evidence is structured JSON,
not text) and only responses with quality `good`: 875 QA and 900 Summary test responses, of
which 160 and 204 are hallucinated. Files `response.jsonl` sha256
`e4c2e4ac24fff676d8984cc61c35d791612fadc58015335d97dd632375e18073`, `source_info.jsonl`
`0dffc26ea9f3c1c3d7c7e8336b56ef1646e3cec876edffcca3c9c624d12d578b`. Data is not copied here.

Protocol, fixed in advance: AUROC on the test split (threshold-free), plus a threshold fitted on the
train split and applied once to test. Nothing is tuned on test. Reproduce with
`python scripts/ragtruth_benchmark.py DIR` (about a minute).

## Results

| Task | Evaluator | AUROC (test) | Accuracy at train-fitted threshold | Accuracy at 1.0 |
| --- | --- | ---: | ---: | ---: |
| QA | `lexical_groundedness` | **0.76** | 74.3% | 18.7% |
| QA | `strict_grounding` | 0.53 | 81.7% (threshold 0, predicts "supported" for all) | 18.9% |
| Summary | `lexical_groundedness` | **0.68** | 77.9% | 22.9% |
| Summary | `strict_grounding` | 0.58 | 77.3% (threshold 0, predicts "supported" for all) | 23.0% |

Majority-class accuracy is 81.7% (QA) and 77.3% (Summary). An AUROC of 0.5 is chance.

## What this shows

- **`strict_grounding` is not suitable for long, abstractive answers.** It is near chance
  (AUROC 0.53 and 0.58) and the best threshold learned on train is 0, meaning "accept everything".
  At the natural threshold of 1.0 it blocks about 81% of all responses, good ones included, because a
  long answer almost always contains one clause that no single evidence sentence supports verbatim.
- **`lexical_groundedness` carries some signal** (AUROC 0.76 and 0.68), but at train-fitted
  thresholds it does not beat always predicting the majority class on accuracy, so it is a weak
  detector. Its signal helps rank responses for review; it should not be the only release gate.
- Together with `docs/case-study-halueval.md`: on short-form QA both lexical evaluators land
  around 91–93%, and on long-form answers they are weak. The earlier 93% figure applies only to
  short, sentence-form claims like our own benchmark.

## Guidance

1. Use `strict_grounding` for short factual answers (numbers, identifiers, negation, single-claim
   sentences). Do not use it as a gate for long summaries or multi-paragraph answers.
2. For long-form answers, rank with lexical groundedness for triage and rely on a calibrated
   semantic scorer (`--evaluator semantic_grounding`) or human review for the decision.
3. Whatever you choose, fit and check the threshold on your own labeled responses with
   `ragops calibrate`.
