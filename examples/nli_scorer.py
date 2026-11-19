#!/usr/bin/env python3
"""Local NLI (entailment) scorer for `ragops evaluate --evaluator semantic_grounding`.

Optional: needs `pip install torch transformers`; RAGOps itself stays dependency-free.
Reads {"evidence": [...], "claim": "..."} on stdin and prints {"score": P(entailment)}, the
highest entailment probability of the claim against any window of the evidence.

    export RAGOPS_NLI_MODEL=cross-encoder/nli-deberta-v3-small   # default
    ragops evaluate --scenario s.json --responses r.json \
        --evaluator semantic_grounding \
        --semantic-command "python examples/nli_scorer.py"

Each call loads the model, so for large runs wrap it in a long-lived service instead.
Measured accuracy is in docs/semantic-evaluator.md; it is not a universal improvement.
"""

import json
import os
import sys

WINDOW_WORDS, STRIDE_WORDS, BATCH = 180, 120, 8


def windows(texts: list[str]) -> list[str]:
    out: list[str] = []
    for text in texts:
        words = text.split()
        starts = range(0, max(len(words) - WINDOW_WORDS + STRIDE_WORDS, 1), STRIDE_WORDS)
        out.extend(" ".join(words[i : i + WINDOW_WORDS]) for i in starts)
    return [w for w in out if w]


def main() -> None:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    request = json.load(sys.stdin)
    name = os.environ.get("RAGOPS_NLI_MODEL", "cross-encoder/nli-deberta-v3-small")
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSequenceClassification.from_pretrained(name).eval()
    entailment = next(i for i, label in model.config.id2label.items() if label.lower().startswith("entail"))
    premises = windows([str(item) for item in request["evidence"]])
    best = 0.0
    for start in range(0, len(premises), BATCH):
        batch = premises[start : start + BATCH]
        encoded = tokenizer(batch, [request["claim"]] * len(batch), truncation=True,
                            max_length=400, padding=True, return_tensors="pt")
        with torch.no_grad():
            best = max(best, float(model(**encoded).logits.softmax(-1)[:, entailment].max()))
    print(json.dumps({"score": round(best, 4)}))


if __name__ == "__main__":
    main()
