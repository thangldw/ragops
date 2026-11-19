#!/usr/bin/env python3
"""Measure grounding evaluators against the labeled benchmark splits."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ragops.evaluators import lexical_groundedness, strict_grounding  # noqa: E402
from ragops.models import EvalCase, RecordedResponse  # noqa: E402

SPLITS = ("dev", "heldout", "heldout2", "heldout3")


def load(split: str) -> list[dict]:
    path = ROOT / "benchmarks" / "grounding" / f"{split}.json"
    return json.loads(path.read_text(encoding="utf-8"))["items"]


def _case(item: dict) -> tuple[EvalCase, RecordedResponse]:
    case = EvalCase(
        id=item["id"], question="", evidence=(item["evidence"],), required_citation_ids=()
    )
    response = RecordedResponse(
        case_id=item["id"], answer=item["answer"], citation_ids=(), latency_ms=0, cost_usd=0
    )
    return case, response


def scores(items: list[dict]) -> dict[str, list[float]]:
    out: dict[str, list[float]] = {"lexical": [], "strict": []}
    for item in items:
        case, response = _case(item)
        out["lexical"].append(lexical_groundedness(case, response))
        out["strict"].append(strict_grounding(case, response).score)
    return out


def metrics(items: list[dict], values: list[float], threshold: float) -> dict[str, float]:
    predicted = [int(value >= threshold) for value in values]
    labels = [item["label"] for item in items]
    correct = sum(p == y for p, y in zip(predicted, labels, strict=True))
    bad = [(p, y) for p, y in zip(predicted, labels, strict=True) if y == 0]
    good = [(p, y) for p, y in zip(predicted, labels, strict=True) if y == 1]
    return {
        "accuracy": correct / len(items),
        "false_pass_rate": sum(p == 1 for p, _ in bad) / max(len(bad), 1),
        "false_block_rate": sum(p == 0 for p, _ in good) / max(len(good), 1),
    }


def best_threshold(items: list[dict], values: list[float]) -> float:
    candidates = sorted({round(value, 3) for value in values} | {1.0})
    return max(candidates, key=lambda t: (metrics(items, values, t)["accuracy"], t))


def main() -> None:
    data = {split: load(split) for split in SPLITS}
    scored = {split: scores(items) for split, items in data.items()}
    thresholds = {
        "lexical": best_threshold(data["dev"], scored["dev"]["lexical"]),
        "strict": 1.0,
    }
    report = {"thresholds": thresholds}
    for split in SPLITS:
        report[split] = {
            name: metrics(data[split], scored[split][name], thresholds[name])
            for name in ("lexical", "strict")
        }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
