import pytest

from ragops.adapters.provider_metrics import (
    deepeval_scores_to_observations,
    otel_evaluation_events_to_observations,
    ragas_scores_to_observations,
)
from ragops.loader import ContractError


def test_ragas_scores_contract_preserves_order_and_selected_metrics() -> None:
    observations = ragas_scores_to_observations(
        [
            {"faithfulness": 0.91, "answer_relevancy": 0.88, "diagnostic": "ignored"},
            {"faithfulness": 0.93, "answer_relevancy": 0.90, "diagnostic": "ignored"},
        ],
        ["case-1", "case-2"],
        repeat_id="run-0001",
        metric_names=("faithfulness", "answer_relevancy"),
    )

    assert observations[0].case_id == "case-1"
    assert observations[1].metrics == {"faithfulness": 0.93, "answer_relevancy": 0.9}


def test_deepeval_scores_contract_preserves_repeats() -> None:
    observations = deepeval_scores_to_observations(
        [
            {
                "case_id": "case-1",
                "repeat_id": "run-0001",
                "metrics": {"answer_relevancy": 0.89},
            },
            {
                "case_id": "case-1",
                "repeat_id": "run-0002",
                "metrics": {"answer_relevancy": 0.92},
            },
        ],
        metric_names=("answer_relevancy",),
    )

    assert [item.repeat_id for item in observations] == ["run-0001", "run-0002"]


def test_otel_evaluation_events_group_metrics_by_case_and_repeat() -> None:
    events = [
        {
            "attributes": {
                "ragops.case.id": "case-1",
                "ragops.repeat.id": "run-0001",
                "gen_ai.evaluation.name": "faithfulness",
                "gen_ai.evaluation.score.value": 0.94,
            }
        },
        {
            "attributes": {
                "ragops.case.id": "case-1",
                "ragops.repeat.id": "run-0001",
                "gen_ai.evaluation.name": "relevancy",
                "gen_ai.evaluation.score.value": 0.90,
            }
        },
    ]

    observations = otel_evaluation_events_to_observations(events)

    assert observations[0].metrics == {"faithfulness": 0.94, "relevancy": 0.9}


@pytest.mark.parametrize(
    "adapter_call, message",
    [
        (
            lambda: ragas_scores_to_observations(
                [{"faithfulness": 0.9}],
                ["one", "two"],
                repeat_id="run-0001",
                metric_names=("faithfulness",),
            ),
            "must match",
        ),
        (
            lambda: deepeval_scores_to_observations(
                [
                    {
                        "case_id": "one",
                        "repeat_id": "run-0001",
                        "metrics": {"quality": float("nan")},
                    }
                ],
                metric_names=("quality",),
            ),
            "finite",
        ),
        (
            lambda: otel_evaluation_events_to_observations(
                [{"attributes": {"ragops.case.id": "one"}}]
            ),
            "missing required",
        ),
    ],
)
def test_provider_contracts_fail_closed(adapter_call, message) -> None:
    with pytest.raises(ContractError, match=message):
        adapter_call()
