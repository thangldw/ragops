import json
from pathlib import Path

import pytest

from ragops.adapters.trace_import import convert_traces
from ragops.init_project import init_project
from ragops.loader import ContractError, load_scenario

LANGFUSE = {"data": [{
    "id": "tr-1", "input": {"question": "Refund window?"}, "output": "Within 30 days.",
    "latency": 1.25, "totalCost": 0.004,
    "observations": [
        {"type": "RETRIEVER", "output": [{"id": "policy-refund", "text": "Refunds within 30 days."}]},
        {"type": "GENERATION", "output": "ignored because trace output exists"},
    ],
}]}
OPENAI = [{
    "id": "chatcmpl-1",
    "request": {"messages": [
        {"role": "system", "content": "Answer from the context."},
        {"role": "user", "content": "<context>Refunds within 30 days.</context>\nRefund window?"},
    ]},
    "response": {"choices": [{"message": {"role": "assistant", "content": "30 days."}}]},
}, {
    "id": "agent-1",
    "messages": [
        {"role": "user", "content": "Ship to Canada?"},
        {"role": "tool", "tool_call_id": "call_1", "content": "US only."},
    ],
    "choices": [{"message": {"content": "No, US only."}}],
}]
ANTHROPIC = [{
    "id": "msg_1",
    "request": {"messages": [{"role": "user", "content": [
        {"type": "document", "title": "policy-refund", "source": {"type": "text", "data": "Refunds within 30 days."}},
        {"type": "text", "text": "Refund window?"},
    ]}]},
    "response": {"content": [{"type": "text", "text": "30 days.", "citations": [{"document_title": "policy-refund"}]}]},
    "latency_ms": 900,
}]


def test_each_converter_extracts_question_answer_and_contexts() -> None:
    langfuse = convert_traces("langfuse", LANGFUSE["data"])[0]
    assert langfuse["question"] == "Refund window?" and langfuse["latency_ms"] == 1250
    assert langfuse["cost_usd"] == 0.004 and langfuse["contexts"][0]["id"] == "policy-refund"
    first, second = convert_traces("openai", OPENAI)
    assert first["question"] == "Refund window?" and first["contexts"] == ["Refunds within 30 days."]
    assert second["contexts"][0]["id"] == "call_1" and second["answer"] == "No, US only."
    anthropic = convert_traces("anthropic", ANTHROPIC)[0]
    assert anthropic["citation_ids"] == ["policy-refund"] and anthropic["question"] == "Refund window?"


def test_missing_context_is_left_out_not_invented() -> None:
    record = convert_traces("openai", [{"messages": [{"role": "user", "content": "hi"}], "choices": [{"message": {"content": "yo"}}]}])[0]
    assert "contexts" not in record
    assert convert_traces("langfuse", ["junk"]) == [{}]
    with pytest.raises(ContractError, match="Unknown source format"):
        convert_traces("nope", [])


@pytest.mark.parametrize(("fmt", "payload", "cases"), [("langfuse", LANGFUSE, 1), ("openai", OPENAI, 2), ("anthropic", ANTHROPIC, 1)])
def test_init_accepts_each_format_end_to_end(tmp_path: Path, fmt: str, payload, cases: int) -> None:
    source = tmp_path / "export.json"
    source.write_text(json.dumps(payload), encoding="utf-8")
    result = init_project(source, tmp_path / "out", source_format=fmt)
    assert result.cases == cases
    assert len(load_scenario(tmp_path / "out/scenario.json").cases) == cases
