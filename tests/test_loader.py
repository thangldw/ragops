import json

import pytest

from ragops.loader import ContractError, load_responses, load_scenario


def test_rejects_unsupported_schema(tmp_path) -> None:
    path = tmp_path / "scenario.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "9.9",
                "id": "future",
                "name": "Future",
                "thresholds": {
                    "citation_coverage": 1,
                    "lexical_groundedness": 1,
                    "max_latency_ms": 1,
                    "max_cost_usd": 1
                },
                "cases": [{"id": "x", "question": "q", "evidence": [], "required_citation_ids": []}]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ContractError, match="Unsupported scenario schema"):
        load_scenario(path)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -0.1, 1.1, True])
def test_rejects_invalid_ratio_thresholds(tmp_path, value: object) -> None:
    path = tmp_path / "scenario.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "id": "strict",
                "name": "Strict",
                "thresholds": {
                    "citation_coverage": value,
                    "citation_precision": 1,
                    "lexical_groundedness": 1,
                    "max_latency_ms": 1,
                    "max_cost_usd": 1,
                },
                "cases": [
                    {"id": "x", "question": "q", "evidence": [], "required_citation_ids": []}
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ContractError):
        load_scenario(path)


@pytest.mark.parametrize(
    "field, value",
    [("latency_ms", -1), ("latency_ms", True), ("cost_usd", -0.1), ("cost_usd", float("nan"))],
)
def test_rejects_invalid_response_numbers(tmp_path, field: str, value: object) -> None:
    response = {
        "case_id": "x",
        "answer": "a",
        "citation_ids": [],
        "latency_ms": 1,
        "cost_usd": 0.0,
    }
    response[field] = value
    path = tmp_path / "responses.json"
    path.write_text(json.dumps([response]), encoding="utf-8")

    with pytest.raises(ContractError):
        load_responses(path)
