import json
from pathlib import Path

import pytest

from ragops.cli import main
from ragops.loader import ContractError, load_responses, load_scenario
from ragops.mine import flag_reason, mine_failures


def _log(question, answer="Paris.", ctx="Paris is the capital of France.", **extra):
    return {"question": question, "answer": answer, "contexts": [ctx], **extra}


def _baseline(tmp_path: Path):
    scenario = {
        "schema_version": "0.2", "id": "s", "name": "S",
        "thresholds": {"citation_coverage": 0, "citation_precision": 0, "lexical_groundedness": 0,
                       "max_latency_ms": 5000, "max_cost_usd": 1},
        "cases": [{"id": "c1", "question": "What is the capital of France?", "evidence": ["Paris is the capital."],
                   "required_citation_ids": []}],
    }
    responses = [{"case_id": "c1", "answer": "Paris.", "citation_ids": [], "retrieved_ids": [], "latency_ms": 1, "cost_usd": 0}]
    (tmp_path / "scenario.json").write_text(json.dumps(scenario), encoding="utf-8")
    (tmp_path / "responses.json").write_text(json.dumps(responses), encoding="utf-8")
    return tmp_path / "scenario.json", tmp_path / "responses.json"


@pytest.mark.parametrize(
    "record,expected",
    [
        ({"thumbs_down": True}, "thumbs down"),
        ({"escalated": True}, "escalated"),
        ({"feedback": {"escalated": True}}, "escalated"),
        ({"feedback": "Thumbs Down"}, "feedback=Thumbs Down"),
        ({"feedback": {"rating": "bad"}}, "feedback.rating=bad"),
        ({"rating": 2}, "rating=2"),
        ({"rating": 3}, None),
        ({"rating": 1.5}, "rating=1.5"),
        ({"vote": -1}, "vote=-1"),
        ({"vote": 0}, "vote=0"),
        ({"vote": 1}, None),
        ({"thumbs": "down"}, "thumbs=down"),
        ({"feedback": {"score": 1}}, "feedback.score=1"),
        ({"feedback": {"score": 5}}, None),
        ({"thumbs_down": False, "rating": 5}, None),
        ({"rating": True}, None),
        ({}, None),
    ],
)
def test_flag_reason(record, expected):
    assert flag_reason(record) == expected


def test_max_rating_is_configurable():
    assert flag_reason({"rating": 3}) is None
    assert flag_reason({"rating": 3}, max_rating=3) == "rating=3"


def test_mine_adds_only_new_flagged_cases(tmp_path):
    scenario, responses = _baseline(tmp_path)
    logs = tmp_path / "logs.jsonl"
    rows = [
        _log("What is the capital of Spain?", "Lisbon.", "Madrid is the capital of Spain.", thumbs_down=True),
        _log("What is the capital of France?", "Lyon.", thumbs_down=True),       # already in the scenario
        _log("  what IS the capital of spain?", "Porto.", thumbs_down=True),    # duplicate of the first
        _log("Who wrote Hamlet?", "Shakespeare.", "Hamlet was written by Shakespeare."),  # not flagged
        _log("Largest planet?", "Mars.", "Jupiter is the largest planet.", rating=1),
        {"question": "No answer", "thumbs_down": True, "contexts": ["x"]},        # flagged but unusable
        "not an object",
    ]
    logs.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    result = mine_failures(logs, scenario, responses, tmp_path / "out")

    assert [a["question"] for a in result.added] == ["What is the capital of Spain?", "Largest planet?"]
    assert result.added[0]["reason"] == "thumbs down" and result.added[1]["reason"] == "rating=1"
    assert result.total_cases == 3
    assert result.skipped["question already in the scenario"] == 2  # one in the baseline, one repeated flag
    assert result.skipped["not flagged as a failure"] == 1
    assert result.skipped["flagged but unusable: missing answer"] == 1
    assert result.skipped["record is not an object"] == 1
    loaded = load_scenario(tmp_path / "out" / "scenario.json")
    mined = [case for case in loaded.cases if case.category == "mined-feedback"]
    assert len(mined) == 2 and all(case.severity == "high" and "mined" in case.tags for case in mined)
    assert {r.case_id for r in load_responses(tmp_path / "out" / "responses.json")} == {c.id for c in loaded.cases}
    assert json.loads((tmp_path / "out" / "mined.json").read_text())[0]["case_id"]


def test_existing_case_ids_are_never_reused(tmp_path):
    scenario, responses = _baseline(tmp_path)
    logs = tmp_path / "logs.json"
    logs.write_text(json.dumps([_log("New question?", thumbs_down=True, id="c1")]), encoding="utf-8")
    result = mine_failures(logs, scenario, responses, tmp_path / "out")
    ids = [case.id for case in load_scenario(tmp_path / "out" / "scenario.json").cases]
    assert len(ids) == len(set(ids)) == 2 and result.added[0]["case_id"] != "c1"


def test_nothing_to_mine_and_overwrite_are_contract_errors(tmp_path):
    scenario, responses = _baseline(tmp_path)
    logs = tmp_path / "logs.json"
    logs.write_text(json.dumps([_log("Fine?")]), encoding="utf-8")
    with pytest.raises(ContractError, match="No new failures"):
        mine_failures(logs, scenario, responses, tmp_path / "out")
    logs.write_text(json.dumps([_log("Bad?", thumbs_down=True)]), encoding="utf-8")
    mine_failures(logs, scenario, responses, tmp_path / "out")
    with pytest.raises(ContractError, match="Refusing to overwrite"):
        mine_failures(logs, scenario, responses, tmp_path / "out")
    empty = tmp_path / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ContractError, match="No JSON or JSONL records"):
        mine_failures(empty, scenario, responses, tmp_path / "out2")


def test_mine_cli(tmp_path, monkeypatch, capsys):
    scenario, responses = _baseline(tmp_path)
    logs = tmp_path / "logs.json"
    logs.write_text(json.dumps([_log("Bad?", thumbs_down=True)]), encoding="utf-8")
    argv = ["ragops", "mine", "--from", str(logs), "--scenario", str(scenario), "--responses", str(responses),
            "--output", str(tmp_path / "out")]
    monkeypatch.setattr("sys.argv", argv)
    assert main() == 0
    assert json.loads(capsys.readouterr().out)["total_cases"] == 2
    monkeypatch.setattr("sys.argv", argv)
    with pytest.raises(SystemExit, match="mine error"):
        main()
