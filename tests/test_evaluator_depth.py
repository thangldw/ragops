from ragops.engine import evaluate
from ragops.loader import scenario_from_dict
from ragops.models import RecordedResponse
from ragops.plugins import CitationCorrectnessEvaluator, ClaimSupportEvaluator


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
