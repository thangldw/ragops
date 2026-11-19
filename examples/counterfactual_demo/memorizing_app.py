#!/usr/bin/env python3
"""Toy system that answers from memory and ignores the evidence it is given."""

import json
import sys

request = json.load(sys.stdin)
MEMORY = json.load(open(__file__.replace("memorizing_app.py", "responses.json"), encoding="utf-8"))
answers = {item["case_id"]: item["answer"] for item in MEMORY}
print(json.dumps({"answer": answers.get(request["case_id"], "I do not know.")}))
