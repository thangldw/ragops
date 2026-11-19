import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("scripts").resolve()))

import grounding_benchmark as bench  # noqa: E402

from ragops.evaluators import strict_grounding  # noqa: E402
from ragops.models import EvalCase, RecordedResponse  # noqa: E402
from ragops.plugins import StrictGroundingEvaluator  # noqa: E402


def _run(evidence: str, answer: str):
    case = EvalCase("c", "", (evidence,), ())
    response = RecordedResponse("c", answer, (), 0, 0.0)
    return case, response


@pytest.mark.parametrize("split", bench.SPLITS)
def test_strict_grounding_beats_lexical_baseline_on_every_split(split: str) -> None:
    items = bench.load(split)
    scored = bench.scores(items)
    lexical_threshold = bench.best_threshold(bench.load("dev"), bench.scores(bench.load("dev"))["lexical"])
    lexical = bench.metrics(items, scored["lexical"], lexical_threshold)
    strict = bench.metrics(items, scored["strict"], 1.0)

    assert strict["accuracy"] >= 0.85
    assert strict["accuracy"] > lexical["accuracy"] + 0.10
    assert strict["false_pass_rate"] <= 0.12


def test_number_negation_and_identifier_mismatches_are_named() -> None:
    wrong_number = strict_grounding(*_run("Refunds last 30 days.", "Refunds last 60 days."))
    flipped = strict_grounding(*_run("It does not cover water.", "It covers water."))
    wrong_room = strict_grounding(*_run("The meeting is in room B.", "The meeting is in room C."))

    assert wrong_number.number_mismatches == 1
    assert flipped.contradicted_claims == 1
    assert wrong_room.number_mismatches == 1


def test_supported_answers_and_empty_answers() -> None:
    assert strict_grounding(*_run("Reset takes 10 seconds.", "Reset takes 10 seconds.")).score == 1.0
    assert strict_grounding(*_run("Reset takes 10 seconds.", "")).score == 0.0


def test_plugin_emits_specific_findings_and_validates_config() -> None:
    result = StrictGroundingEvaluator().evaluate(*_run("It does not cover water.", "It covers water."))
    assert [f.rule for f in result.findings] == ["contradicted_claim"]
    assert result.metrics["score"] == 0.0
    with pytest.raises(ValueError):
        StrictGroundingEvaluator(min_overlap=2)
