"""``ragops mine``: grow a scenario with the real failures found in production logs.

Records the user flagged (thumbs down, low rating, escalation, "needs review") are appended to an
existing scenario as new high-severity cases, so the regression suite grows with every incident.
The failing answer is kept as the baseline response for the new case; a fixed system should score
better than it, and the case then guards against the failure coming back.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ragops.init_project import _normalize, _question_key, _read_records
from ragops.loader import ContractError, load_responses, load_scenario

TRUE_FLAGS = (
    "thumbs_down", "downvote", "disliked", "escalated", "flagged", "needs_review",
    "feedback.thumbs_down", "feedback.escalated", "feedback.flagged",
)
TEXT_FLAGS = (
    "feedback", "user_feedback", "feedback.rating", "feedback.value", "feedback.label",
    "label", "thumb", "thumbs", "vote", "rating",
)
RATING_KEYS = ("rating", "feedback.rating", "feedback.score", "stars")
VOTE_KEYS = ("thumb", "thumbs", "vote", "feedback.value")
NEGATIVE_WORDS = {
    "negative", "bad", "down", "thumbs_down", "thumbsdown", "thumb_down", "dislike", "disliked",
    "unhelpful", "incorrect", "wrong", "hallucination", "inaccurate", "poor", "escalated",
}


@dataclass
class MineResult:
    added: list[dict[str, str]] = field(default_factory=list)
    skipped: Counter[str] = field(default_factory=Counter)
    files: list[str] = field(default_factory=list)
    total_cases: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "added": self.added,
            "skipped": dict(self.skipped),
            "files": self.files,
            "total_cases": self.total_cases,
            "note": "Mined cases keep the failing answer as the baseline response. Run your fixed system on "
            "every case and compare: it should beat these answers and must not regress on the others.",
        }


def _lookup(record: dict[str, Any], dotted: str) -> Any:
    node: Any = record
    for part in dotted.split("."):
        node = node.get(part) if isinstance(node, dict) else None
        if node is None:
            return None
    return node


def flag_reason(record: dict[str, Any], max_rating: float = 2.0) -> str | None:
    """Why a log record counts as a failure, or None when nothing marks it as one."""
    for key in TRUE_FLAGS:
        if _lookup(record, key) is True:
            return key.rsplit(".", 1)[-1].replace("_", " ")
    for key in TEXT_FLAGS:
        value = _lookup(record, key)
        if isinstance(value, str) and value.strip().casefold().replace(" ", "_") in NEGATIVE_WORDS:
            return f"{key}={value.strip()}"
    for key in VOTE_KEYS:
        value = _lookup(record, key)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value <= 0:
            return f"{key}={value}"
    for key in RATING_KEYS:
        value = _lookup(record, key)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value <= max_rating:
            return f"{key}={value}"
    return None


def mine_failures(
    source: str | Path,
    scenario_path: str | Path,
    responses_path: str | Path,
    output: str | Path,
    *,
    max_rating: float = 2.0,
) -> MineResult:
    load_scenario(scenario_path)
    load_responses(responses_path)
    scenario = json.loads(Path(scenario_path).read_text(encoding="utf-8"))
    responses = json.loads(Path(responses_path).read_text(encoding="utf-8"))
    records = list(_read_records(Path(source)))
    if not records:
        raise ContractError(f"No JSON or JSONL records found in {source}")
    result = MineResult()
    known = {_question_key(case["question"]) for case in scenario["cases"]}
    used = {case["id"] for case in scenario["cases"]}
    new_cases: list[dict[str, Any]] = []
    new_responses: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            result.skipped["record is not an object"] += 1
            continue
        reason = flag_reason(record, max_rating)
        if reason is None:
            result.skipped["not flagged as a failure"] += 1
            continue
        normalized, why_not = _normalize(record, index, used)
        if normalized is None:
            result.skipped[f"flagged but unusable: {why_not}"] += 1
            continue
        case, response = normalized
        key = _question_key(case["question"])
        if key in known:
            used.discard(case["id"])
            result.skipped["question already in the scenario"] += 1
            continue
        known.add(key)
        case.update({"category": "mined-feedback", "severity": "high", "tags": ["mined", "user-flagged"]})
        new_cases.append(case)
        new_responses.append(response)
        result.added.append({"case_id": case["id"], "question": case["question"], "reason": reason})
    if not new_cases:
        raise ContractError(f"No new failures to add. Skipped: {dict(result.skipped)}")
    scenario["cases"] = [*scenario["cases"], *new_cases]
    root = Path(output)
    root.mkdir(parents=True, exist_ok=True)
    scenario_out, responses_out = root / "scenario.json", root / "responses.json"
    mined_out = root / "mined.json"
    for path in (scenario_out, responses_out, mined_out):
        if path.exists():
            raise ContractError(f"Refusing to overwrite {path}")
    scenario_out.write_text(json.dumps(scenario, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    responses_out.write_text(
        json.dumps([*responses, *new_responses], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    mined_out.write_text(json.dumps(result.added, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    load_responses(responses_out)
    result.total_cases = len(load_scenario(scenario_out).cases)
    result.files = [str(scenario_out), str(responses_out), str(mined_out)]
    return result
