#!/usr/bin/env python3
"""Do the explorer's highlighted words line up with RAGTruth's annotated hallucination spans?

Character-level, test split, quality `good`, QA and Summary. Precision is the share of highlighted
characters inside annotated spans; recall the share of annotated characters that are highlighted.
`lift` divides precision by the share of annotated characters among all characters of the same
responses (what highlighting at random would score).

    python scripts/ragtruth_span_check.py DATA_DIR
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ragops.evaluators import unsupported_spans  # noqa: E402


def covered(spans: list[tuple[int, int]], length: int) -> list[bool]:
    mask = [False] * length
    for start, end in spans:
        for index in range(max(start, 0), min(end, length)):
            mask[index] = True
    return mask


def main() -> None:
    root = Path(sys.argv[1])
    sources = {}
    for line in (root / "source_info.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record["task_type"] in {"QA", "Summary"}:
            info = record["source_info"]
            sources[record["source_id"]] = (
                record["task_type"], info.get("passages", "") if isinstance(info, dict) else info
            )
    totals: dict[str, dict[str, int]] = {}
    for line in (root / "response.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["split"] != "test" or row.get("quality") != "good" or row["source_id"] not in sources:
            continue
        task, evidence = sources[row["source_id"]]
        text = row["response"]
        highlighted = covered(unsupported_spans(text, (evidence,)), len(text))
        gold = covered([(label["start"], label["end"]) for label in row["labels"]], len(text))
        bucket = totals.setdefault(task, {"hit": 0, "highlighted": 0, "gold": 0, "chars": 0,
                                          "clean_chars": 0, "clean_highlighted": 0})
        bucket["hit"] += sum(h and g for h, g in zip(highlighted, gold, strict=True))
        bucket["highlighted"] += sum(highlighted)
        bucket["gold"] += sum(gold)
        bucket["chars"] += len(text)
        if not row["labels"]:
            bucket["clean_chars"] += len(text)
            bucket["clean_highlighted"] += sum(highlighted)
    report = {}
    for task, t in sorted(totals.items()):
        precision = t["hit"] / t["highlighted"] if t["highlighted"] else 0.0
        base = t["gold"] / t["chars"]
        report[task] = {
            "precision": round(precision, 4),
            "recall": round(t["hit"] / t["gold"], 4),
            "random_precision": round(base, 4),
            "lift": round(precision / base, 2),
            "share_of_clean_text_highlighted": round(t["clean_highlighted"] / t["clean_chars"], 4),
            "share_of_all_text_highlighted": round(t["highlighted"] / t["chars"], 4),
        }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
