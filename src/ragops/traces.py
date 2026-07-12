from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from ragops.loader import ContractError
from ragops.models import RecordedResponse


def load_trace_jsonl(path: str | Path) -> tuple[RecordedResponse, ...]:
    """Load the portable RAGOps trace envelope from newline-delimited JSON."""
    records: list[RecordedResponse] = []
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ContractError(f"Cannot load traces from {path}: {exc}") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            item: dict[str, Any] = json.loads(line)
            usage = item.get("usage", {})
            records.append(
                RecordedResponse(
                    case_id=item["case_id"],
                    answer=item["output"]["answer"],
                    citation_ids=tuple(item["output"].get("citation_ids", [])),
                    retrieved_ids=tuple(item.get("retrieval", {}).get("document_ids", [])),
                    latency_ms=item["latency_ms"],
                    cost_usd=usage.get("cost_usd", 0.0),
                    human_approved=item.get("human_approved", False),
                    metadata={
                        "trace_schema_version": item.get("schema_version", "0.3"),
                        **item.get("metadata", {}),
                    },
                )
            )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise ContractError(f"Invalid trace at line {line_number}: {exc}") from exc
    if not records:
        raise ContractError("Trace file contains no records")
    return tuple(records)


def write_trace_jsonl(path: str | Path, traces: Iterable[dict[str, Any]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(trace, ensure_ascii=False) + "\n" for trace in traces),
        encoding="utf-8",
    )
