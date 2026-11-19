import json
from pathlib import Path

import pytest

from ragops.cli import main
from ragops.init_project import init_project
from ragops.loader import ContractError, load_responses, load_scenario

LOGS = [
    {"id": "t1", "input": {"question": "Refund window?"}, "output": "Refunds within 30 days.",
     "retrieved_contexts": [{"id": "policy-refund", "page_content": "Refunds within 30 days of purchase."}],
     "citations": ["policy-refund"], "latency_ms": 800, "usage": {"cost_usd": 0.002}},
    {"query": "Ship to Canada?", "response": "Yes, in 3 days.", "documents": ["We ship to the US only."], "latency": 1500},
    {"query": "no answer", "documents": ["x"]},
    "not an object",
]


def _write(tmp_path: Path) -> Path:
    path = tmp_path / "logs.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in LOGS), encoding="utf-8")
    return path


def test_init_builds_loadable_scenario_and_runs_first_report(tmp_path: Path) -> None:
    result = init_project(_write(tmp_path), tmp_path / "out")
    assert result.cases == 2 and sum(result.skipped.values()) == 2
    scenario = load_scenario(tmp_path / "out/scenario.json")
    assert len(scenario.cases) == 2
    assert scenario.cases[0].required_citation_ids == ("policy-refund",)
    assert load_responses(tmp_path / "out/responses.json")[1].latency_ms == 1500
    assert (tmp_path / "out/first-report.md").read_text().startswith("# RAGOps evaluation")
    assert "strict_grounding.unsupported_claims" in result.metrics


def test_init_reads_a_directory_and_json_arrays(tmp_path: Path) -> None:
    folder = tmp_path / "logs"
    folder.mkdir()
    (folder / "a.json").write_text(json.dumps(LOGS[:2]), encoding="utf-8")
    (folder / "ignored.txt").write_text("nope", encoding="utf-8")
    assert init_project(folder, tmp_path / "out").cases == 2


def test_init_refuses_overwrite_unusable_and_symlink_input(tmp_path: Path) -> None:
    logs = _write(tmp_path)
    init_project(logs, tmp_path / "out")
    with pytest.raises(ContractError, match="overwrite"):
        init_project(logs, tmp_path / "out")
    bad = tmp_path / "bad.json"
    bad.write_text('[{"foo": 1}]', encoding="utf-8")
    with pytest.raises(ContractError, match="No usable records"):
        init_project(bad, tmp_path / "out2")
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    with pytest.raises(ContractError, match="not valid JSON"):
        init_project(broken, tmp_path / "out3")
    link = tmp_path / "link.jsonl"
    link.symlink_to(logs)
    with pytest.raises(ContractError, match="symlink"):
        init_project(link, tmp_path / "out4")


def test_init_cli(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr("sys.argv", ["ragops", "init", "--from", str(_write(tmp_path)), "--output", str(tmp_path / "o")])
    assert main() == 0
    assert json.loads(capsys.readouterr().out)["cases"] == 2
    monkeypatch.setattr("sys.argv", ["ragops", "init", "--from", str(tmp_path / "missing"), "--output", str(tmp_path / "o2")])
    with pytest.raises(SystemExit):
        main()
