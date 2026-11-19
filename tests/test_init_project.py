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


def _log(question: str, answer: str, context: str, ident: str | None = None) -> dict:
    record = {"query": question, "response": answer, "documents": [context], "latency": 900}
    if ident:
        record["id"] = ident
    return record


def test_init_with_candidate_logs_writes_a_comparison(tmp_path: Path) -> None:
    base = tmp_path / "before.jsonl"
    cand = tmp_path / "after.jsonl"
    base.write_text("\n".join(json.dumps(r) for r in [
        _log("Refund window?", "Refunds are available within 30 days.", "Refunds are available within 30 days of purchase."),
        _log("Ship to Canada?", "We ship to the US only.", "We ship to the US only."),
        _log("Only in baseline?", "Yes it is.", "Yes it is."),
    ]), encoding="utf-8")
    cand.write_text("\n".join(json.dumps(r) for r in [
        _log("  ship TO canada?  ", "Yes, we ship to Canada in 3 days.", "irrelevant"),
        _log("Refund window?", "Refunds are available within 30 days.", "x"),
        _log("Brand new question", "Something.", "x"),
    ]), encoding="utf-8")
    result = init_project(base, tmp_path / "out", candidate=cand)
    assert result.cases == 2
    assert result.skipped["candidate has no matching baseline case"] == 1
    assert result.skipped["baseline case without a candidate answer"] == 1
    out = tmp_path / "out"
    assert {p.name for p in out.iterdir()} >= {"scenario.json", "responses.json", "candidate.json", "compare-report.md"}
    assert "Canada" in (out / "candidate.json").read_text(encoding="utf-8")
    assert (out / "compare-report.md").read_text(encoding="utf-8").startswith("# RAGOps")
    assert not result.passed


def test_init_candidate_with_no_overlap_is_rejected(tmp_path: Path) -> None:
    base = tmp_path / "a.jsonl"
    cand = tmp_path / "b.jsonl"
    base.write_text(json.dumps(_log("one?", "A.", "A.")), encoding="utf-8")
    cand.write_text(json.dumps(_log("two?", "B.", "B.")), encoding="utf-8")
    with pytest.raises(ContractError, match="No candidate record matched"):
        init_project(base, tmp_path / "out", candidate=cand)
    cand.write_text(json.dumps({"id": "x"}) + "\n" + json.dumps(_log("one?", "", "A.")) + "\n[1]", encoding="utf-8")
    with pytest.raises(ContractError):
        init_project(base, tmp_path / "out2", candidate=cand)
