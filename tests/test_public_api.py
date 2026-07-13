from ragops import __version__, responses_from_data, scenario_from_dict


def test_stable_version() -> None:
    assert __version__ == "2.2.0"


def test_public_contract_parsers() -> None:
    scenario = scenario_from_dict(
        {
            "schema_version": "0.1",
            "id": "public",
            "name": "Public API",
            "thresholds": {
                "citation_coverage": 1,
                "lexical_groundedness": 0,
                "max_latency_ms": 1000,
                "max_cost_usd": 1,
            },
            "cases": [
                {"id": "one", "question": "q", "evidence": [], "required_citation_ids": []}
            ],
        }
    )
    responses = responses_from_data(
        [{"case_id": "one", "answer": "a", "latency_ms": 1, "cost_usd": 0}]
    )

    assert scenario.id == "public"
    assert responses[0].case_id == "one"
