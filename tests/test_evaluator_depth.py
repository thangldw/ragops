from dataclasses import replace

from ragops.engine import evaluate
from ragops.loader import scenario_from_dict
from ragops.models import EvaluationPolicy, MetricGate, RecordedResponse
import pytest

from ragops.plugins import (
    AbstentionContractEvaluator,
    AnswerLengthBudgetEvaluator,
    CitationCorrectnessEvaluator,
    ClaimSupportEvaluator,
    SourceFreshnessEvaluator,
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


def test_plugin_metric_and_high_finding_can_block_release() -> None:
    response = RecordedResponse(
        "q1",
        "Stop the machine. Replace the controller immediately.",
        ("manual-1",),
        1,
        0,
    )
    report = evaluate(
        _scenario(),
        (response,),
        evaluators=(ClaimSupportEvaluator(),),
        policy=EvaluationPolicy(
            metric_gates={"claim_support": MetricGate(minimum=0.9)},
            fail_on_severity="high",
        ),
    )

    assert report.passed is False
    assert report.metrics["claim_support"] == report.metrics["claim_support.score"] == 0.5
    assert "metric_minimum:claim_support" in report.failed_gates
    assert "finding_severity:high" in report.failed_gates


def test_policy_fails_closed_for_unavailable_metric() -> None:
    response = RecordedResponse("q1", "Stop the machine.", ("manual-1",), 1, 0)

    with pytest.raises(ValueError, match="unavailable"):
        evaluate(
            _scenario(),
            (response,),
            policy=EvaluationPolicy(metric_gates={"claim_support": MetricGate(minimum=0.9)}),
        )


def test_python_policy_rejects_ambiguous_metric_direction() -> None:
    response = RecordedResponse("q1", "Stop the machine.", ("manual-1",), 1, 0)

    with pytest.raises(ValueError, match="exactly one"):
        evaluate(
            _scenario(),
            (response,),
            evaluators=(ClaimSupportEvaluator(),),
            policy=EvaluationPolicy(
                metric_gates={"claim_support": MetricGate(minimum=0.8, maximum=1.0)}
            ),
        )


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


def test_source_freshness_checks_exact_current_source_contract() -> None:
    case = replace(_scenario().cases[0], tags=("freshness",))
    scenario = replace(_scenario(), cases=(case,))
    stale = RecordedResponse("q1", "Stop the machine.", ("manual-old",), 1, 0)

    report = evaluate(scenario, (stale,), evaluators=(SourceFreshnessEvaluator(),))

    assert report.metrics["source_freshness.score"] == 0.0
    assert report.cases[0].findings[0].rule == "stale_source_contract_violation"


def test_abstention_contract_requires_cited_lexical_support() -> None:
    case = replace(
        _scenario().cases[0],
        evidence=("No approved repair procedure is available.",),
        tags=("abstain",),
    )
    scenario = replace(_scenario(), cases=(case,))
    invented = RecordedResponse("q1", "Replace the controller immediately.", (), 1, 0)

    report = evaluate(scenario, (invented,), evaluators=(AbstentionContractEvaluator(),))

    assert report.metrics["abstention_contract.score"] == 0.0
    assert report.cases[0].findings[0].rule == "abstention_contract_violation"


def test_specialized_contract_evaluators_are_neutral_for_untagged_cases() -> None:
    response = RecordedResponse("q1", "Anything", (), 1, 0)

    report = evaluate(
        _scenario(),
        (response,),
        evaluators=(SourceFreshnessEvaluator(), AbstentionContractEvaluator()),
    )

    assert report.metrics["source_freshness.score"] == 1.0
    assert report.metrics["abstention_contract.score"] == 1.0
    assert report.cases[0].findings == ()
