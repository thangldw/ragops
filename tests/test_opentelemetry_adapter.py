from __future__ import annotations

import json
from pathlib import Path

import pytest

from examples.opentelemetry_trace_adapter.adapter import (
    SpanContractError,
    convert_spans,
    main,
    span_to_trace,
)
from ragops.traces import load_trace_jsonl


FIXTURE = Path("examples/opentelemetry_trace_adapter/spans.jsonl")


def _span(**attribute_overrides: object) -> dict[str, object]:
    attributes: dict[str, object] = {
        "ragops.case_id": "case-1",
        "gen_ai.prompt": "What happened?",
        "gen_ai.response.text": "A cited answer.",
    }
    attributes.update(attribute_overrides)
    return {"duration_ms": 42, "attributes": attributes}


def test_span_to_trace_maps_required_and_optional_fields() -> None:
    trace = span_to_trace(
        _span(
            **{
                "service.name": "support-agent",
                "ragops.citation_ids": "doc-1, doc-2",
                "ragops.retrieved_document_ids": ["doc-1"],
                "ragops.cost_usd": 0.01,
                "ragops.human_approved": True,
            }
        )
    )

    assert trace["schema_version"] == "0.4"
    assert trace["output"]["citation_ids"] == ["doc-1", "doc-2"]
    assert trace["retrieval"]["document_ids"] == ["doc-1"]
    assert trace["latency_ms"] == 42
    assert trace["human_approved"] is True
    assert trace["metadata"]["application"] == "support-agent"


@pytest.mark.parametrize(
    ("span", "message"),
    [
        ({"duration_ms": 1, "attributes": {}}, "ragops.case_id"),
        (_span(**{"ragops.citation_ids": 42}), "string or string list"),
        ({**_span(), "duration_ms": -1}, "non-negative"),
    ],
)
def test_span_to_trace_fails_closed(span: dict[str, object], message: str) -> None:
    with pytest.raises(SpanContractError, match=message):
        span_to_trace(span)


def test_convert_spans_rejects_empty_input() -> None:
    with pytest.raises(SpanContractError, match="no records"):
        convert_spans([])


def test_example_cli_writes_loadable_trace_04(tmp_path: Path) -> None:
    output = tmp_path / "traces.jsonl"

    assert main(["--input", str(FIXTURE), "--output", str(output)]) == 0

    traces = load_trace_jsonl(output)
    raw = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert [trace.case_id for trace in traces] == ["error-e42", "escalation-e42"]
    assert all(item["schema_version"] == "0.4" for item in raw)
    assert traces[0].metadata["trace_schema_version"] == "0.4"
