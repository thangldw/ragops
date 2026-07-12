from ragops.engine import evaluate
from ragops.loader import scenario_from_dict
from ragops.models import RecordedResponse
import pytest

from ragops.plugins import (
    AnswerLengthBudgetEvaluator,
    CitationCorrectnessEvaluator,
    ClaimSupportEvaluator,
)


def _scenario():
    return scenario_from_dict(
        {
            "schema_version": "0.2",
            "id": "calibration",
            "name": "Evaluator calibration",
            "thresholds": {
                "citation_coverage": 0,
                "citation_precision": 0,
                "lexical_groundedness": 0,
                "max_latency_ms": 1000,
                "max_cost_usd": 1,
            },
            "cases": [
                {
                    "id": "q1",
                    "question": "Procedure?",
                    "evidence": ["Stop the machine. Inspect the cooling fan."],
                    "required_citation_ids": ["manual-1"],
                    "category": "direct_procedure",
                    "severity": "high",
                    "language": "en",
                }
            ],
        }
    )


def test_claim_support_calibration_supported_answer() -> None:
    response = RecordedResponse("q1", "Stop the machine. Inspect the cooling fan.", ("manual-1",), 1, 0)
    report = evaluate(_scenario(), (response,), evaluators=(ClaimSupportEvaluator(),))

    assert report.metrics["claim_support.score"] == 1.0
    assert report.metrics["claim_support.unsupported_claims"] == 0.0
    assert report.cases[0].findings == ()


def test_claim_support_calibration_flags_added_claim() -> None:
    response = RecordedResponse(
        "q1",
        "Stop the machine. Replace the controller immediately.",
        ("manual-1",),
        1,
        0,
    )
    report = evaluate(_scenario(), (response,), evaluators=(ClaimSupportEvaluator(),))

    assert report.metrics["claim_support.score"] == 0.5
    assert report.metrics["claim_support.unsupported_claims"] == 1.0
    assert report.cases[0].findings[0].rule == "unsupported_claim"


def test_citation_correctness_flags_untrusted_id() -> None:
    response = RecordedResponse("q1", "Stop the machine.", ("manual-1", "fake-2"), 1, 0)
    report = evaluate(_scenario(), (response,), evaluators=(CitationCorrectnessEvaluator(),))

    assert report.metrics["citation_correctness.score"] == 0.5
    assert report.cases[0].findings[0].rule == "unsupported_citation"


def test_answer_length_budget_counts_unicode_code_points_at_boundary() -> None:
    response = RecordedResponse("q1", "短い回答", ("manual-1",), 1, 0)
    report = evaluate(
        _scenario(),
        (response,),
        evaluators=(AnswerLengthBudgetEvaluator(max_characters=4),),
    )

    assert report.passed is True
    assert report.metrics["answer_length_budget.character_count"] == 4.0
    assert report.metrics["answer_length_budget.within_budget"] == 1.0
    assert report.cases[0].findings == ()


def test_answer_length_budget_reports_noncritical_excess_without_blocking() -> None:
    response = RecordedResponse("q1", "12345", ("manual-1",), 1, 0)
    report = evaluate(
        _scenario(),
        (response,),
        evaluators=(AnswerLengthBudgetEvaluator(max_characters=4),),
    )

    assert report.passed is True
    assert report.metrics["answer_length_budget.within_budget"] == 0.0
    assert report.cases[0].findings[0].rule == "answer_length_budget_exceeded"
    assert report.cases[0].findings[0].severity == "medium"


@pytest.mark.parametrize("limit", [0, -1])
def test_answer_length_budget_rejects_nonpositive_limit(limit: int) -> None:
    with pytest.raises(ValueError, match="positive"):
        AnswerLengthBudgetEvaluator(max_characters=limit)


def test_answer_length_budget_rejects_boolean_limit() -> None:
    with pytest.raises(TypeError, match="integer"):
        AnswerLengthBudgetEvaluator(max_characters=True)
