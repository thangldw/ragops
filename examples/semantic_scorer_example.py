#!/usr/bin/env python3
"""Example semantic scorer for `ragops evaluate --evaluator semantic_grounding`.

Reads {"evidence": [...], "claim": "..."} on stdin and prints {"score": 0..1}.
Swap `similarity` for your embedding model or LLM judge; RAGOps itself stays
dependency-free. This toy version uses character-trigram cosine similarity so it
runs anywhere, and is NOT a real semantic model.

    ragops evaluate --scenario s.json --responses r.json \
        --evaluator semantic_grounding \
        --semantic-command "python examples/semantic_scorer_example.py"
"""

import json
import math
import sys
from collections import Counter


def grams(text: str) -> Counter:
    text = " ".join(text.casefold().split())
    return Counter(text[i : i + 3] for i in range(max(len(text) - 2, 1)))


def similarity(evidence: str, claim: str) -> float:
    a, b = grams(evidence), grams(claim)
    dot = sum(a[g] * b[g] for g in a)
    norm = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return dot / norm if norm else 0.0


if __name__ == "__main__":
    request = json.load(sys.stdin)
    best = max((similarity(e, request["claim"]) for e in request["evidence"]), default=0.0)
    print(json.dumps({"score": round(min(best, 1.0), 4)}))
