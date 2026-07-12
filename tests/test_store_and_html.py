from ragops.engine import compare
from ragops.loader import load_responses, load_scenario
from ragops.reporters import comparison_html
from ragops.store import ExperimentStore

SCENARIO = "scenarios/japanese_troubleshooting/scenario.json"
RESPONSES = "scenarios/japanese_troubleshooting/sample_responses.json"


def test_store_round_trip(tmp_path) -> None:
    scenario = load_scenario(SCENARIO)
    responses = load_responses(RESPONSES)
    report = compare(scenario, responses, responses)
    store = ExperimentStore(tmp_path / "runs.db")

    run_id = store.save(report, label="main", metadata={"commit": "abc123"})

    runs = store.list_runs()
    assert runs[0]["id"] == run_id
    assert runs[0]["metadata"]["commit"] == "abc123"
    assert store.get_report(run_id)["passed"] is True


def test_html_report_is_standalone_and_escaped() -> None:
    scenario = load_scenario(SCENARIO)
    responses = load_responses(RESPONSES)
    report = compare(scenario, responses, responses)

    rendered = comparison_html(report)

    assert rendered.startswith("<!doctype html>")
    assert "RAGOps regression report" in rendered
    assert "<table>" in rendered
    assert "Candidate case drill-down" in rendered
    assert "Citation precision" in rendered
    assert "error-e42" in rendered
