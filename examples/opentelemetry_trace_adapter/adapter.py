from __future__ import annotations

import argparse
import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from ragops.traces import write_trace_jsonl


class SpanContractError(ValueError):
    """Raised when an exported span cannot become a portable RAGOps trace."""


def _required_text(attributes: Mapping[str, Any], name: str) -> str:
    value = attributes.get(name)
    if not isinstance(value, str) or not value.strip():
        raise SpanContractError(f"Span attribute {name!r} must be a non-empty string")
    return value.strip()


def _string_list(attributes: Mapping[str, Any], name: str) -> list[str]:
    value = attributes.get(name, [])
    if value is None:
        return []
    if isinstance(value, str):
        values: Sequence[Any] = [part.strip() for part in value.split(",") if part.strip()]
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        values = value
    else:
        raise SpanContractError(f"Span attribute {name!r} must be a string or string list")
    if any(not isinstance(item, str) or not item.strip() for item in values):
        raise SpanContractError(f"Span attribute {name!r} contains a non-string value")
    return [item.strip() for item in values]


def _number(attributes: Mapping[str, Any], name: str, default: float = 0.0) -> float:
    value = attributes.get(name, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise SpanContractError(f"Span attribute {name!r} must be a non-negative number")
    return float(value)


def _latency_ms(span: Mapping[str, Any]) -> int:
    if "duration_ms" in span:
        duration = span["duration_ms"]
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or duration < 0:
            raise SpanContractError("Span duration_ms must be a non-negative number")
        return round(duration)

    start = span.get("start_time_unix_nano")
    end = span.get("end_time_unix_nano")
    if (
        isinstance(start, bool)
        or isinstance(end, bool)
        or not isinstance(start, int)
        or not isinstance(end, int)
        or end < start
    ):
        raise SpanContractError(
            "Span needs non-negative duration_ms or ordered integer nanosecond timestamps"
        )
    return round((end - start) / 1_000_000)


def span_to_trace(span: Mapping[str, Any]) -> dict[str, Any]:
    """Map one filtered, exported OpenTelemetry span to trace schema 0.4."""
    attributes = span.get("attributes")
    if not isinstance(attributes, Mapping):
        raise SpanContractError("Span attributes must be an object")

    metadata = {
        key: value
        for key, attribute in {
            "application": "service.name",
            "build": "service.version",
            "retriever": "ragops.retriever",
            "generator": "gen_ai.request.model",
            "role": "ragops.role",
        }.items()
        if isinstance((value := attributes.get(attribute)), str) and value.strip()
    }
    for name in ("trace_id", "span_id"):
        value = span.get(name)
        if isinstance(value, str) and value:
            metadata[name] = value

    trace: dict[str, Any] = {
        "schema_version": "0.4",
        "case_id": _required_text(attributes, "ragops.case_id"),
        "input": {"question": _required_text(attributes, "gen_ai.prompt")},
        "output": {
            "answer": _required_text(attributes, "gen_ai.response.text"),
            "citation_ids": _string_list(attributes, "ragops.citation_ids"),
        },
        "retrieval": {
            "document_ids": _string_list(attributes, "ragops.retrieved_document_ids")
        },
        "latency_ms": _latency_ms(span),
        "usage": {"cost_usd": _number(attributes, "ragops.cost_usd")},
        "human_approved": attributes.get("ragops.human_approved") is True,
        "metadata": metadata,
    }
    decision = attributes.get("ragops.decision")
    if isinstance(decision, str) and decision.strip():
        trace["output"]["decision"] = decision.strip()
    return trace


def convert_spans(spans: Iterable[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    """Convert a sequence while preserving order and fail closed on invalid spans."""
    converted = tuple(span_to_trace(span) for span in spans)
    if not converted:
        raise SpanContractError("Span input contains no records")
    return converted


def _read_jsonl(path: Path) -> tuple[Mapping[str, Any], ...]:
    records: list[Mapping[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise SpanContractError(f"Cannot read spans from {path}: {exc}") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SpanContractError(f"Invalid span JSON at line {line_number}: {exc}") from exc
        if not isinstance(record, Mapping):
            raise SpanContractError(f"Span at line {line_number} must be an object")
        records.append(record)
    return tuple(records)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert exported OTel spans to RAGOps traces")
    parser.add_argument("--input", type=Path, required=True, help="Filtered span JSONL")
    parser.add_argument("--output", type=Path, required=True, help="RAGOps trace JSONL")
    args = parser.parse_args(argv)
    try:
        traces = convert_spans(_read_jsonl(args.input))
        write_trace_jsonl(args.output, traces)
    except SpanContractError as exc:
        parser.exit(2, f"error: {exc}\n")
    print(f"Wrote {len(traces)} portable traces to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
