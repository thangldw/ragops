import json
from pathlib import Path

from ragops.cli import main


def test_answer_length_evaluator_cli_uses_configured_limit(
    monkeypatch, capsys, tmp_path: Path
) -> None:
    output = tmp_path / "report.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "ragops",
            "evaluate",
            "--scenario",
            "scenarios/japanese_troubleshooting/scenario.json",
            "--responses",
            "scenarios/japanese_troubleshooting/sample_responses.json",
            "--evaluator",
            "answer_length_budget",
            "--answer-length-limit",
            "10",
            "--output",
            str(output),
        ],
    )

    assert main() == 0
    assert capsys.readouterr().out == ""
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["metrics"]["answer_length_budget.within_budget"] == 0.0
    assert all(
        case["findings"][0]["rule"] == "answer_length_budget_exceeded"
        for case in report["cases"]
    )
