#!/usr/bin/env python3
"""Blind relabeling workflow for the grounding benchmark.

export  -> a labeling sheet without the maintainer's labels or failure kinds
ingest  -> validate reviewer sheets, report agreement, and build a calibration set

    python scripts/grounding_labels.py export --out sheet.json
    # give sheet.json to a reviewer; they fill "label" with 0 or 1 and return it
    python scripts/grounding_labels.py ingest --sheet alice.json --sheet bob.json \
        --evaluator strict --calibration-out calibration.json
    ragops calibrate --input calibration.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import grounding_benchmark as bench  # noqa: E402

from ragops.calibration import (  # noqa: E402
    CalibrationPolicy,
    CalibrationRecord,
    HumanLabel,
    calibrate_evaluator,
)


class LabelError(ValueError):
    pass


def all_items() -> list[dict]:
    return [item for split in bench.SPLITS for item in bench.load(split)]


def export_sheet(reviewer: str = "") -> dict:
    return {
        "schema": "ragops-grounding-label-sheet-0.1",
        "reviewer": reviewer,
        "instructions": (
            "For each item set label to 1 if the answer is FULLY supported by the evidence "
            "(every claim, every number, no contradiction), otherwise 0. Use only the evidence."
        ),
        "items": [
            {"id": it["id"], "language": it["language"], "evidence": it["evidence"],
             "answer": it["answer"], "label": None}
            for it in all_items()
        ],
    }


def load_sheet(path: str | Path, known_ids: set[str]) -> tuple[str, dict[str, int]]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LabelError(f"Cannot read sheet {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema") != "ragops-grounding-label-sheet-0.1":
        raise LabelError(f"{path}: unsupported sheet schema")
    reviewer = data.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise LabelError(f"{path}: reviewer must be a non-empty string")
    labels: dict[str, int] = {}
    for item in data.get("items", []):
        item_id, label = item.get("id"), item.get("label")
        if item_id not in known_ids:
            raise LabelError(f"{path}: unknown item id {item_id!r}")
        if item_id in labels:
            raise LabelError(f"{path}: duplicate item id {item_id}")
        if isinstance(label, bool) or label not in (0, 1):
            raise LabelError(f"{path}: item {item_id} label must be 0 or 1")
        labels[item_id] = label
    if set(labels) != known_ids:
        raise LabelError(f"{path}: expected labels for all {len(known_ids)} items")
    return reviewer.strip(), labels


def ingest(sheets: list[str], evaluator: str) -> tuple[dict, dict]:
    items = all_items()
    known = {it["id"] for it in items}
    reviewers = {"maintainer": {it["id"]: it["label"] for it in items}}
    for path in sheets:
        name, labels = load_sheet(path, known)
        if name in reviewers:
            raise LabelError(f"duplicate reviewer name {name!r}")
        reviewers[name] = labels
    dev = bench.load("dev")
    threshold = 1.0 if evaluator == "strict" else bench.best_threshold(
        dev, bench.scores(dev)["lexical"]
    )
    # The evaluator's pass/fail decision (1.0 or 0.0) is what gets calibrated.
    decisions = [float(value >= threshold) for value in bench.scores(items)[evaluator]]
    records = tuple(
        CalibrationRecord(
            it["id"], decision,
            tuple(HumanLabel(name, labels[it["id"]]) for name, labels in reviewers.items()),
        )
        for it, decision in zip(items, decisions, strict=True)
    )
    policy = CalibrationPolicy(0.5, 1.0, 0.0, 1.0, 1.0, 0.0)
    report = calibrate_evaluator(evaluator, records, policy)
    maintainer = reviewers["maintainer"]
    disagreements = [
        {"id": i, "maintainer": maintainer[i],
         "reviewers": {n: given[i] for n, given in reviewers.items() if n != "maintainer"}}
        for i in sorted(maintainer)
        if len({given[i] for given in reviewers.values()}) > 1
    ]
    calibration = {
        "schema_version": "1.0",
        "evaluator": evaluator,
        "policy": {
            "threshold": 0.5, "minimum_coverage": 1.0, "minimum_accuracy": 0.8,
            "maximum_mae": 0.5, "maximum_false_pass_rate": 0.1, "minimum_agreement": 0.6,
        },
        "records": [
            {"case_id": r.case_id, "automated_score": r.automated_score,
             "human_labels": [{"reviewer": h.reviewer, "label": h.label} for h in r.human_labels]}
            for r in records
        ],
    }
    summary = {
        "reviewers": sorted(reviewers),
        "items": len(items),
        "reviewer_agreement_kappa": report.reviewer_agreement,
        "disagreement_count": len(disagreements),
        "disagreements": disagreements,
    }
    return summary, calibration


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export")
    export.add_argument("--out", required=True)
    export.add_argument("--reviewer", default="")
    ing = sub.add_parser("ingest")
    ing.add_argument("--sheet", action="append", required=True)
    ing.add_argument("--evaluator", choices=("strict", "lexical"), default="strict")
    ing.add_argument("--calibration-out")
    args = parser.parse_args()
    try:
        if args.command == "export":
            Path(args.out).write_text(
                json.dumps(export_sheet(args.reviewer), ensure_ascii=False, indent=1) + "\n",
                encoding="utf-8",
            )
            return 0
        summary, calibration = ingest(args.sheet, args.evaluator)
    except LabelError as exc:
        print(f"label error: {exc}", file=sys.stderr)
        return 1
    if args.calibration_out:
        Path(args.calibration_out).write_text(
            json.dumps(calibration, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
