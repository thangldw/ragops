import json

from ragops.benchmarks import scenario_summary
from ragops.cli import main
from ragops.loader import load_scenario


def test_scenario_summary_exposes_coverage() -> None:
    summary = scenario_summary(load_scenario("scenarios/japanese_troubleshooting/scenario.json"))

    assert summary["schema_version"] == "0.2"
    assert summary["case_count"] == 2
    assert summary["categories"] == {
        "direct_procedure": 1,
        "escalation_decision": 1,
    }
    assert summary["languages"] == {"ja": 2}


def test_cli_inspect_prints_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "inspect",
            "--scenario",
            "scenarios/japanese_troubleshooting/scenario.json",
        ],
    )

    assert main() == 0
    output = json.loads(capsys.readouterr().out)
    assert output["scenario_id"] == "jp-troubleshooting-v1"
