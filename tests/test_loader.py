import json

import pytest

from ragops.loader import ContractError, load_scenario


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

