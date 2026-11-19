#!/usr/bin/env python3
"""Zero-shot check of the grounding evaluators on HaluEval QA (public, MIT).

Protocol fixed before looking at results: no thresholds are tuned on this data. The
lexical threshold is the one chosen on our own dev split; strict_grounding uses 1.0.

    curl -L -o qa_data.json \
      https://raw.githubusercontent.com/RUCAIBox/HaluEval/main/data/qa_data.json
    python scripts/public_benchmark.py qa_data.json
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from grounding_benchmark import best_threshold, load, scores  # noqa: E402

from ragops.evaluators import lexical_groundedness, strict_grounding  # noqa: E402
from ragops.models import EvalCase, RecordedResponse  # noqa: E402


def wilson(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return 0.0, 0.0
    p = successes / total
    centre = p + z * z / (2 * total)
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total))
    denom = 1 + z * z / total
    return (centre - margin) / denom, (centre + margin) / denom


def evaluate_pairs(rows: list[dict]) -> dict:
    dev = load("dev")
    lexical_threshold = best_threshold(dev, scores(dev)["lexical"])
    outcome = {"lexical": {"good_pass": 0, "bad_pass": 0}, "strict": {"good_pass": 0, "bad_pass": 0}}
    for index, row in enumerate(rows):
        case = EvalCase(id=str(index), question=row["question"], evidence=(row["knowledge"],), required_citation_ids=())
        for key, answer in (("good_pass", row["right_answer"]), ("bad_pass", row["hallucinated_answer"])):
            response = RecordedResponse(str(index), answer, (), 0, 0)
            outcome["lexical"][key] += lexical_groundedness(case, response) >= lexical_threshold
            outcome["strict"][key] += strict_grounding(case, response).score >= 1.0
    total = len(rows)
    report = {"pairs": total, "lexical_threshold": lexical_threshold}
    for name, counts in outcome.items():
        low, high = wilson(counts["bad_pass"], total)
        block_low, block_high = wilson(total - counts["good_pass"], total)
        report[name] = {
            "false_pass_rate": counts["bad_pass"] / total,
            "false_pass_ci95": [round(low, 4), round(high, 4)],
            "false_block_rate": (total - counts["good_pass"]) / total,
            "false_block_ci95": [round(block_low, 4), round(block_high, 4)],
            "accuracy": (counts["good_pass"] + total - counts["bad_pass"]) / (2 * total),
        }
    return report


def main() -> None:
    path = Path(sys.argv[1])
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    report = evaluate_pairs(rows)
    report["source_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
