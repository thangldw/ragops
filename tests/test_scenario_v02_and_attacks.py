from dataclasses import replace

import pytest

from ragops.engine import compare, evaluate
from ragops.loader import ContractError, load_attack_pack, scenario_from_dict
from ragops.models import RecordedResponse


def _scenario():
    return scenario_from_dict(
        {
            "schema_version": "0.2",
            "id": "citation-v02",
            "name": "Citation precision",
            "thresholds": {
                "citation_coverage": 1.0,
                "citation_precision": 1.0,
                "lexical_groundedness": 1.0,
                "max_latency_ms": 1000,
                "max_cost_usd": 0.01,
            },
            "cases": [
                {
                    "id": "q1",
                    "question": "対応は？",
                    "evidence": ["Stop the machine."],
                    "required_citation_ids": ["manual-1"],
                    "category": "direct_procedure",
                    "severity": "high",
                    "language": "ja",
                    "tags": ["safety"],
                }
            ],
        }
    )


def test_scenario_v02_metadata_and_citation_precision() -> None:
    scenario = _scenario()
    response = RecordedResponse(
        case_id="q1",
        answer="Stop the machine.",
        citation_ids=("manual-1",),
        latency_ms=100,
        cost_usd=0.001,
    )

    report = evaluate(scenario, (response,))

    assert report.passed is True
    assert report.metrics["citation_precision"] == 1.0
    assert scenario.cases[0].category == "direct_procedure"
    assert scenario.cases[0].tags == ("safety",)


def test_citation_stuffing_fails_precision_and_regression() -> None:
    scenario = _scenario()
    baseline = RecordedResponse("q1", "Stop the machine.", ("manual-1",), 100, 0.001)
    stuffed = replace(baseline, citation_ids=("manual-1", "unrelated-9"))

    report = compare(scenario, (baseline,), (stuffed,))

    assert report.candidate.metrics["citation_coverage"] == 1.0
    assert report.candidate.metrics["citation_precision"] == 0.5
    assert "citation_precision" in report.candidate.failed_gates
    assert "citation_precision_regression" in report.failed_gates


def test_loads_portable_attack_pack() -> None:
    pack = load_attack_pack("scenarios/japanese_troubleshooting/attack-pack.json")

    assert len(pack.attacks) == 6
    assert pack.attacks[0].severity == "critical"
    assert {attack.category for attack in pack.attacks} >= {
        "direct_prompt_injection",
        "permission_leakage",
        "excessive_agency",
    }


def test_attack_pack_rejects_invalid_severity(tmp_path) -> None:
    path = tmp_path / "attacks.json"
    path.write_text(
        '{"schema_version":"0.1","id":"x","name":"x","attacks":'
        '[{"id":"a","category":"x","input_text":"x","expected_rule":"x",'
        '"severity":"urgent"}]}',
        encoding="utf-8",
    )

    with pytest.raises(ContractError, match="severity"):
        load_attack_pack(path)
