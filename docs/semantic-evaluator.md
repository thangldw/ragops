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
