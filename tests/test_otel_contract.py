import pytest

from ragops.adapters.otel_genai import otel_spans_to_trace_graph
from ragops.loader import ContractError


def _span(**overrides):
    span = {
        "trace_id": "t1", "span_id": "s1", "name": "step",
        "start_time_unix_nano": 1_000_000_000, "end_time_unix_nano": 2_000_000_000,
        "attributes": {},
    }
    span.update(overrides)
    return span


def test_minimal_span_converts_with_adapter_metadata() -> None:
    graph = otel_spans_to_trace_graph([_span()]).to_dict()
    assert graph["trace_id"] == "t1"
    assert graph["metadata"]["adapter"] == "otel-genai"
    assert graph["spans"][0]["operation"] == "step"


def test_tool_and_agent_names_take_precedence_and_children_keep_parent() -> None:
    parent = _span(attributes={"gen_ai.agent.name": "planner", "gen_ai.operation.name": "invoke_agent"})
    child = _span(
        span_id="s2", parent_span_id="s1", name="x",
        attributes={"gen_ai.tool.name": "search", "gen_ai.operation.name": "execute_tool"},
    )
    graph = otel_spans_to_trace_graph([parent, child]).to_dict()
    assert [s["operation"] for s in graph["spans"]] == ["planner", "search"]
    assert graph["spans"][1]["parent_id"] == "s1"


@pytest.mark.parametrize(
    "spans",
    [
        [],
        [_span(trace_id="")],
        [_span(), _span(trace_id="other")],
        [_span(attributes=["not", "a", "map"])],
        [_span(name="", attributes={})],
        [_span(start_time_unix_nano="soon")],
        [_span(end_time_unix_nano=None)],
        [_span(start_time_unix_nano=True)],
    ],
)
def test_malformed_exports_fail_with_contract_error(spans) -> None:
    with pytest.raises(ContractError):
        otel_spans_to_trace_graph(spans)


def test_non_object_span_is_rejected() -> None:
    with pytest.raises(ContractError, match="must be an object"):
        otel_spans_to_trace_graph(["not-a-span"])
