import sqlite3

from ragops.engine import evaluate
from ragops.loader import load_responses, load_scenario
from ragops.store import ExperimentStore


def _report():
    return evaluate(
        load_scenario("scenarios/japanese_troubleshooting/scenario.json"),
        load_responses("scenarios/japanese_troubleshooting/sample_responses.json"),
    )


def test_run_review_and_history(tmp_path) -> None:
    store = ExperimentStore(tmp_path / "runs.db")
    run_id = store.save(_report(), label="candidate-a")

    store.review(run_id, status="accepted", reviewer="thang", note="M4 baseline")

    run = store.list_runs()[0]
    assert run["review_status"] == "accepted"
    assert run["reviewer"] == "thang"
    assert run["review_note"] == "M4 baseline"


def test_metric_trend_orders_oldest_to_newest(tmp_path) -> None:
    store = ExperimentStore(tmp_path / "runs.db")
    first = store.save(_report(), label="first")
    second = store.save(_report(), label="second")

    points = store.metric_trend("jp-troubleshooting-v1", "citation_coverage")

    assert [point["run_id"] for point in points] == [first, second]
    assert [point["value"] for point in points] == [1.0, 1.0]


def test_review_rejects_unknown_run_and_status(tmp_path) -> None:
    store = ExperimentStore(tmp_path / "runs.db")

    try:
        store.review("missing", status="accepted", reviewer="thang")
    except KeyError:
        pass
    else:
        raise AssertionError("unknown run must fail")

    run_id = store.save(_report())
    try:
        store.review(run_id, status="maybe", reviewer="thang")
    except ValueError:
        pass
    else:
        raise AssertionError("invalid status must fail")


def test_legacy_store_migrates_review_columns(tmp_path) -> None:
    path = tmp_path / "legacy.db"
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE runs (
                id TEXT PRIMARY KEY, created_at TEXT NOT NULL, scenario_id TEXT NOT NULL,
                report_type TEXT NOT NULL, passed INTEGER NOT NULL, label TEXT NOT NULL,
                metadata TEXT NOT NULL, report TEXT NOT NULL
            )
            """
        )

    store = ExperimentStore(path)
    run_id = store.save(_report())
    store.review(run_id, status="accepted", reviewer="thang")

    assert store.list_runs()[0]["review_status"] == "accepted"
