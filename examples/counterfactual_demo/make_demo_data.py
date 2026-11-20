#!/usr/bin/env python3
"""Regenerate scenario.json and responses.json (the baseline answers of faithful_app.py)."""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
CASES = [
    ("refund", "How many days do customers have to request a refund?", ["Customers can request a refund within 30 days of purchase.", "Shipping is free for orders over 50 dollars."]),
    ("warranty", "How long is the warranty on laptops?", ["Laptops carry a warranty of 24 months from delivery.", "Accessories carry a warranty of 6 months."]),
    ("support", "What hours is phone support open?", ["Phone support is open from 9 to 17 on weekdays.", "Email support answers within 2 days."]),
    ("shipping", "What is the free shipping threshold?", ["Shipping is free for orders over 50 dollars.", "Express delivery costs 12 dollars."]),
    ("returns", "Who pays for return shipping?", ["The customer pays for return shipping unless the item is defective.", "Defective items are replaced free of charge."]),
    ("privacy", "How long is personal data retained?", ["Personal data is retained for 36 months after the last order."]),
    ("sizes", "What sizes does the jacket come in?", ["The jacket comes in sizes small, medium and large."]),
    ("loyalty", "How many points does a purchase earn?", ["Each purchase earns 5 loyalty points per 10 dollars spent.", "Points expire after 12 months."]),
]


def ask(case_id, question, evidence):
    out = subprocess.run(
        [sys.executable, str(HERE / "faithful_app.py")],
        input=json.dumps({"case_id": case_id, "question": question, "evidence": evidence}).encode(),
        capture_output=True, check=True,
    ).stdout
    return json.loads(out)["answer"]


scenario_cases, responses = [], []
for case_id, question, evidence in CASES:
    answer = ask(case_id, question, evidence)
    ids = [f"{case_id}-p{i}" for i in range(1, len(evidence) + 1)]
    cited = [ids[i] for i, passage in enumerate(evidence) if answer in passage][:1]
    scenario_cases.append({"id": case_id, "question": question, "evidence": evidence, "required_citation_ids": cited})
    responses.append({"case_id": case_id, "answer": answer, "citation_ids": cited, "retrieved_ids": ids, "latency_ms": 1, "cost_usd": 0})
scenario = {
    "schema_version": "0.2", "id": "cf-demo", "name": "Counterfactual demo",
    "thresholds": {"citation_coverage": 0, "citation_precision": 0, "lexical_groundedness": 0, "max_latency_ms": 5000, "max_cost_usd": 1},
    "cases": scenario_cases,
}
(HERE / "scenario.json").write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
(HERE / "responses.json").write_text(json.dumps(responses, indent=2) + "\n", encoding="utf-8")
print(f"wrote {len(CASES)} cases")
