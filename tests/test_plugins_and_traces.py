import pytest

from ragops.engine import evaluate
from ragops.loader import ContractError, load_scenario
from ragops.plugins import EvaluatorRegistry, RetrievalRecallEvaluator
from ragops.traces import load_trace_jsonl

SCENARIO = "scenarios/japanese_troubleshooting/scenario.json"
TRACES = "scenarios/japanese_troubleshooting/sample_traces.jsonl"


def test_trace_import_and_retrieval_plugin() -> None:
    report = evaluate(
        load_scenario(SCENARIO),
        load_trace_jsonl(TRACES),
        evaluators=(RetrievalRecallEvaluator(),),
    )

    assert report.passed is True
    assert report.cases[0].custom_metrics["retrieval_recall.score"] == 1.0


def test_registry_rejects_duplicate_evaluator_names() -> None:
    registry = EvaluatorRegistry()
    registry.register(RetrievalRecallEvaluator())

    with pytest.raises(ValueError, match="unique"):
        registry.register(RetrievalRecallEvaluator())


def test_trace_loader_reports_line_number(tmp_path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text("{}\nnot-json\n", encoding="utf-8")

    with pytest.raises(ContractError, match="line 1"):
        load_trace_jsonl(path)
