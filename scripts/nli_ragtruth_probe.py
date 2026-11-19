"""Probe: off-the-shelf NLI models vs lexical grounding on RAGTruth (needs torch, transformers).

    python scripts/nli_ragtruth_probe.py MODEL N QA|Summary DATA_DIR [windows|bm25]

[windows|bm25] chooses how evidence is picked per claim. DATA_DIR holds response.jsonl and source_info.jsonl (see ragtruth_benchmark.py). Response score is the
minimum over sentences of the best entailment probability over sliding evidence windows.
"""

from __future__ import annotations

import json
import math
import random
import re
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from ragtruth_benchmark import auroc  # noqa: E402

from ragops.evaluators import lexical_groundedness, split_sentences  # noqa: E402
from ragops.models import EvalCase, RecordedResponse  # noqa: E402


def windows(text: str, size: int = 180, stride: int = 120) -> list[str]:
    words = text.split()
    starts = range(0, max(len(words) - size + stride, 1), stride)
    return [" ".join(words[i : i + size]) for i in starts] or [""]


def top_sentences(text: str, claim: str, k: int = 3) -> list[str]:
    """Pick the k evidence sentences with the highest IDF-weighted overlap with the claim."""
    sentences = split_sentences(text) or [text]
    docs = [set(re.findall(r"\w+", s.casefold())) for s in sentences]
    idf = {t: math.log(1 + len(docs) / (1 + sum(t in d for d in docs))) for d in docs for t in d}
    wanted = set(re.findall(r"\w+", claim.casefold()))
    ranked = sorted(range(len(sentences)), key=lambda i: -sum(idf[t] for t in docs[i] & wanted))
    chosen = sorted(ranked[:k])
    return [" ".join(sentences[i] for i in chosen)]


def main() -> None:
    name, count, task, data = sys.argv[1], int(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
    select = sys.argv[5] if len(sys.argv) > 5 else "windows"
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSequenceClassification.from_pretrained(name).eval()
    entail = next(i for i, label in model.config.id2label.items() if label.lower().startswith("entail"))
    sources = {}
    for line in (data / "source_info.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record["task_type"] == task:
            info = record["source_info"]
            sources[record["source_id"]] = info if task == "Summary" else info.get("passages", "")
    rows = [json.loads(line) for line in (data / "response.jsonl").read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["split"] == "test" and r["source_id"] in sources and r.get("quality") == "good"]
    random.Random(1).shuffle(rows)
    rows = rows[:count]

    def best_entailment(premises: list[str], hypothesis: str) -> float:
        best = 0.0
        for start in range(0, len(premises), 8):
            batch = premises[start : start + 8]
            encoded = tokenizer(batch, [hypothesis] * len(batch), truncation=True, max_length=400,
                                padding=True, return_tensors="pt")
            with torch.no_grad():
                best = max(best, float(model(**encoded).logits.softmax(-1)[:, entail].max()))
        return best

    started = time.time()
    nli, mean, lexical, labels = [], [], [], []
    for row in rows:
        premises = windows(sources[row["source_id"]])
        sentences = split_sentences(row["response"])[:12]
        per_sentence = [
            best_entailment(top_sentences(sources[row["source_id"]], s) if select == "bm25" else premises, s)
            for s in sentences
        ]
        nli.append(min(per_sentence, default=0.0))
        mean.append(sum(per_sentence) / len(per_sentence) if per_sentence else 0.0)
        labels.append(int(not row["labels"]))
        case = EvalCase("x", "", (sources[row["source_id"]],), ())
        lexical.append(lexical_groundedness(case, RecordedResponse("x", row["response"], (), 0, 0)))
    print(f"{task} n={len(rows)} hallucinated={len(rows) - sum(labels)} seconds={round(time.time() - started)}")
    print("AUROC nli-min", round(auroc(nli, labels), 4), "nli-mean", round(auroc(mean, labels), 4),
          "lexical", round(auroc(lexical, labels), 4))


if __name__ == "__main__":
    main()
