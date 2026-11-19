#!/usr/bin/env python3
"""Toy extractive RAG: answers with the evidence sentence that best matches the question."""

import json
import re
import sys

request = json.load(sys.stdin)
words = set(re.findall(r"\w+", request["question"].casefold()))
sentences = [s.strip() for passage in request["evidence"] for s in re.split(r"(?<=[.!?])\s+", passage) if s.strip()]
best = max(sentences, key=lambda s: len(words & set(re.findall(r"\w+", s.casefold()))), default="")
overlap = len(words & set(re.findall(r"\w+", best.casefold()))) if best else 0
print(json.dumps({"answer": best if overlap >= 2 else "I do not know."}))
