# Semantic grounding (plug-in)

`lexical_groundedness` and `strict_grounding` are lexical and miss synonym paraphrases ([accuracy](evaluator-accuracy.md)). `semantic_grounding` delegates the judgement to a scorer you supply, so the core stays offline and dependency-free.

```bash
ragops evaluate --scenario s.json --responses r.json \
  --evaluator semantic_grounding \
  --semantic-command "python my_scorer.py"
```

The command runs once per claim, without a shell. It reads `{"evidence": [...], "claim": "..."}` on stdin and prints `{"score": 0.0-1.0}`. Non-zero exits, timeouts, malformed JSON and out-of-range scores fail the run. A claim is supported when its score is at least the threshold (default 0.5).

**Guard:** by default a claim is never supported if it states a number or identifier missing from the evidence, or flips polarity/antonyms, because embedding and LLM scorers often miss exactly those errors. In Python pass `guard_with_strict=False` to disable.

See `examples/semantic_scorer_example.py` (a toy trigram scorer; replace with your embedding model or LLM judge). Always measure your scorer with `ragops calibrate` against your own human labels before gating on it; RAGOps does not claim any particular accuracy for a scorer it does not ship.

## Measured: off-the-shelf NLI is not a drop-in fix

`examples/nli_scorer.py` scores a claim by the best entailment probability over sliding windows of the
evidence (local NLI model; needs `torch` and `transformers`, not a RAGOps dependency). We measured it with
`scripts/nli_ragtruth_probe.py` on 150 randomly chosen RAGTruth QA test responses (28 hallucinated),
response score = minimum over sentences of the best window entailment:

| Scorer | AUROC (RAGTruth QA, n=150) |
| --- | ---: |
| `lexical_groundedness` | 0.76 |
| `cross-encoder/nli-deberta-v3-small` | 0.68 |
| `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli` | 0.62 |

On 500 HaluEval pairs the small model scored AUROC 0.58 (short answers are not claims, so NLI has little to
work with). Small sample, one aggregation rule, no tuning: treat these as a warning, not a ranking.
The windowing, sentence splitting and aggregation matter a lot, and long abstractive answers are hard for
sentence-level NLI. Do not assume a semantic scorer beats lexical grounding: measure it on your own labeled
responses with `ragops calibrate` before gating on it.

Follow-up on the small model (same 150 responses): choosing the three best evidence sentences per claim by IDF-weighted overlap instead of sliding windows gave AUROC 0.68 (unchanged), and averaging sentence scores instead of taking the minimum gave 0.63. Evidence selection and aggregation are not what limits off-the-shelf NLI here; the models themselves are. A stronger judge (a larger model behind `--semantic-command`) remains untested.
