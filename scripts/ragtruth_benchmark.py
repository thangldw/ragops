#!/usr/bin/env python3
"""Check grounding evaluators on RAGTruth (public) at response level.

A response counts as hallucinated when RAGTruth lists at least one annotated hallucination
span. QA and Summary tasks only: Data2txt evidence is structured JSON, not text.
Protocol, fixed in advance: report AUROC (threshold-free) and also a threshold fitted on
the *train* split and applied once to the *test* split. Nothing is tuned on test.

    D=https://raw.githubusercontent.com/ParticleMedia/RAGTruth/main/dataset
    curl -L -O $D/response.jsonl -O $D/source_info.jsonl
    python scripts/ragtruth_benchmark.py DIR
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ragops.evaluators import lexical_groundedness, strict_grounding  # noqa: E402
from ragops.models import EvalCase, RecordedResponse  # noqa: E402

TASKS = {"QA", "Summary"}


def auroc(scores: list[float], labels: list[int]) -> float:
    """Probability a random supported (label 1) response outscores a hallucinated one."""
    pairs = sorted(zip(scores, labels, strict=True))
    rank_sum, i = 0.0, 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        rank_sum += sum(label for _, label in pairs[i:j]) * ((i + 1 + j) / 2)
        i = j
    positives = sum(labels)
    negatives = len(labels) - positives
    return (rank_sum - positives * (positives + 1) / 2) / (positives * negatives)


def accuracy(scores: list[float], labels: list[int], threshold: float) -> float:
    return sum((s >= threshold) == bool(y) for s, y in zip(scores, labels, strict=True)) / len(labels)


def best_threshold(scores: list[float], labels: list[int]) -> float:
    return max(sorted(set(scores)), key=lambda t: (accuracy(scores, labels, t), t))


def evidence_text(task: str, info: object) -> str:
    if task == "QA" and isinstance(info, dict):
        return str(info.get("passages", ""))
    return info if isinstance(info, str) else ""


def main() -> None:
    root = Path(sys.argv[1])
    sources = {}
    for line in (root / "source_info.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record["task_type"] in TASKS:
            sources[record["source_id"]] = (record["task_type"], evidence_text(record["task_type"], record["source_info"]))
    data: dict[str, dict[str, dict[str, list]]] = {}
    for line in (root / "response.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record["source_id"] not in sources or record.get("quality") != "good":
            continue
        task, evidence = sources[record["source_id"]]
        case = EvalCase(record["id"], "", (evidence,), ())
        response = RecordedResponse(record["id"], record["response"], (), 0, 0)
        bucket = data.setdefault(record["split"], {}).setdefault(task, {"lexical": [], "strict": [], "label": []})
        bucket["lexical"].append(lexical_groundedness(case, response))
        bucket["strict"].append(strict_grounding(case, response).score)
        bucket["label"].append(int(not record["labels"]))
    report: dict[str, object] = {
        "source_sha256": {n: hashlib.sha256((root / n).read_bytes()).hexdigest() for n in ("response.jsonl", "source_info.jsonl")}
    }
    for task in sorted(TASKS):
        train, test = data["train"][task], data["test"][task]
        entry: dict[str, object] = {"test_responses": len(test["label"]), "test_hallucinated": len(test["label"]) - sum(test["label"])}
        for name in ("lexical", "strict"):
            threshold = best_threshold(train[name], train["label"])
            entry[name] = {
                "auroc_test": round(auroc(test[name], test["label"]), 4),
                "threshold_fit_on_train": round(threshold, 4),
                "accuracy_test_at_that_threshold": round(accuracy(test[name], test["label"], threshold), 4),
                "accuracy_test_at_1.0": round(accuracy(test[name], test["label"], 1.0), 4),
            }
        majority = max(sum(test["label"]), len(test["label"]) - sum(test["label"])) / len(test["label"])
        entry["majority_class_accuracy"] = round(majority, 4)
        report[task] = entry
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
