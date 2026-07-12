import json

from examples.japanese_troubleshooting_agent.agent import TroubleshootingAgent
from ragops.engine import compare, evaluate
from ragops.loader import load_scenario
from ragops.plugins import CitationCorrectnessEvaluator, ClaimSupportEvaluator
from ragops.traces import load_trace_jsonl, write_trace_jsonl


def test_reference_agent_answers_and_respects_acl() -> None:
    agent = TroubleshootingAgent()

    result = agent.ask("A1000 E-42 の一次対応は？", role="engineer")
    restricted = agent.retrieve("A1000 E-42 PRIVATE_EXECUTIVE_NOTE", role="engineer", top_k=10)

    assert result.citation_ids == ("manual-a1000-e42",)
    assert result.decision == "answer"
    assert "executive-incident-note" not in {hit.document.id for hit in restricted}


def test_reference_agent_requires_approval_for_external_action() -> None:
    result = TroubleshootingAgent().ask("顧客へ復旧メールを送信して。", role="engineer")

    assert result.decision == "request_approval"
    assert result.citation_ids == ("policy-external-email",)
    assert "sending email" in result.answer


def test_reference_suite_exports_passing_ragops_traces(tmp_path) -> None:
    agent = TroubleshootingAgent()
    suite = json.loads(
        open("examples/japanese_troubleshooting_agent/suite.json", encoding="utf-8").read()
    )
    output = tmp_path / "traces.jsonl"
    write_trace_jsonl(
        output,
        [agent.trace(case["case_id"], case["question"], role=case["role"]) for case in suite],
    )

    responses = load_trace_jsonl(output)
    report = evaluate(
        load_scenario("examples/japanese_troubleshooting_agent/scenario.json"),
        responses,
        evaluators=(CitationCorrectnessEvaluator(), ClaimSupportEvaluator()),
    )

    assert report.passed is True
    assert report.metrics["citation_correctness.score"] == 1.0
    assert responses[0].metadata["retriever"] == "lexical-graph-acl-v1"
    assert responses[0].metadata["trace_schema_version"] == "0.4"


def test_lexical_only_candidate_regresses_against_graph_retrieval(tmp_path) -> None:
    suite = json.loads(
        open("examples/japanese_troubleshooting_agent/suite.json", encoding="utf-8").read()
    )
    graph = TroubleshootingAgent(graph_enabled=True)
    lexical = TroubleshootingAgent(graph_enabled=False)
    graph_path = tmp_path / "graph.jsonl"
    lexical_path = tmp_path / "lexical.jsonl"
    write_trace_jsonl(
        graph_path,
        [graph.trace(case["case_id"], case["question"], role=case["role"]) for case in suite],
    )
    write_trace_jsonl(
        lexical_path,
        [lexical.trace(case["case_id"], case["question"], role=case["role"]) for case in suite],
    )

    report = compare(
        load_scenario("examples/japanese_troubleshooting_agent/scenario.json"),
        load_trace_jsonl(graph_path),
        load_trace_jsonl(lexical_path),
    )

    assert report.passed is False
    assert "candidate_release_gate" in report.failed_gates
