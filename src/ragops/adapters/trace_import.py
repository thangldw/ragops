"""Convert LLM-platform trace exports into the generic record shape ``ragops init`` reads.

Supported: Langfuse trace exports, OpenAI chat-completion logs, Anthropic Messages logs.
Each converter returns plain dicts with ``id``, ``question``, ``answer``, ``contexts``,
``citation_ids``, ``latency_ms`` and ``cost_usd`` where the source has them. Nothing
is invented: a record with no retrieved context is returned without ``contexts`` and
``ragops init`` then skips it and says why. Cost is only taken when the export carries it;
token counts are never converted to money with guessed prices.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from ragops.loader import ContractError

TAG_BLOCK = re.compile(
    r"<(?P<tag>context|documents?|sources?|retrieved_context)>(?P<body>.*?)</(?P=tag)>",
    re.DOTALL | re.IGNORECASE,
)


def convert_traces(source_format: str, records: list[Any]) -> list[dict[str, Any]]:
    converter = CONVERTERS.get(source_format)
    if converter is None:
        raise ContractError(f"Unknown source format {source_format!r}; use one of {sorted(CONVERTERS)}")
    converted = []
    for record in records:
        if isinstance(record, dict):
            converted.append(converter(record))
        else:
            converted.append({})
    return converted


def _text(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        for key in ("question", "query", "text", "content", "answer", "output", "input"):
            found = _text(value.get(key))
            if found:
                return found
    if isinstance(value, list):
        parts = [_text(item) for item in value]
        joined = "\n".join(part for part in parts if part)
        return joined or None
    return None


def _last_message(messages: Any, role: str) -> str | None:
    if not isinstance(messages, list):
        return None
    for message in reversed(messages):
        if isinstance(message, dict) and message.get("role") == role:
            text = _blocks_text(message.get("content"))
            if text:
                return text
    return None


def _blocks_text(content: Any) -> str | None:
    if isinstance(content, str):
        return content.strip() or None
    if isinstance(content, list):
        parts = [
            b["text"].strip()
            for b in content
            if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str)
        ]
        joined = "\n".join(part for part in parts if part)
        return joined or None
    return None


def _split_tagged_context(question: str | None) -> tuple[str | None, list[str]]:
    if not question:
        return question, []
    contexts = [m.group("body").strip() for m in TAG_BLOCK.finditer(question) if m.group("body").strip()]
    stripped = TAG_BLOCK.sub("", question).strip()
    return stripped or question, contexts


def _section(record: dict[str, Any], key: str) -> dict[str, Any]:
    value = record.get(key)
    return value if isinstance(value, dict) else record


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 or value != value:
        return None
    return float(value)


def _clean(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if value not in (None, "", [])}


def from_langfuse(trace: dict[str, Any]) -> dict[str, Any]:
    contexts: list[Any] = []
    cited: list[str] = []
    answer = _text(trace.get("output"))
    cost = _number(trace.get("totalCost"))
    for observation in trace.get("observations") or []:
        if not isinstance(observation, dict):
            continue
        kind = str(observation.get("type", "")).upper()
        if kind == "RETRIEVER":
            output = observation.get("output")
            documents = output.get("documents") if isinstance(output, dict) else output
            if isinstance(documents, list):
                contexts.extend(documents)
        elif kind == "GENERATION" and answer is None:
            answer = _text(observation.get("output"))
    latency = _number(trace.get("latency"))
    return _clean(
        {
            "id": trace.get("id"),
            "question": _text(trace.get("input")),
            "answer": answer,
            "contexts": contexts,
            "citation_ids": cited,
            "latency_ms": None if latency is None else int(latency * 1000),
            "cost_usd": cost,
        }
    )


def from_openai(record: dict[str, Any]) -> dict[str, Any]:
    request, response = _section(record, "request"), _section(record, "response")
    messages = request.get("messages")
    question = _last_message(messages, "user")
    question, tagged = _split_tagged_context(question)
    contexts: list[Any] = list(tagged)
    if isinstance(messages, list):
        for message in messages:
            if isinstance(message, dict) and message.get("role") == "tool":
                text = _blocks_text(message.get("content"))
                if text:
                    contexts.append({"id": message.get("tool_call_id"), "text": text})
    answer = None
    choices = response.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        message = choices[0].get("message")
        answer = _blocks_text(message.get("content")) if isinstance(message, dict) else None
    return _clean(
        {
            "id": record.get("id") or response.get("id"),
            "question": question,
            "answer": answer,
            "contexts": contexts,
            "latency_ms": _number(record.get("latency_ms")),
            "cost_usd": _number(record.get("cost_usd")),
        }
    )


def from_anthropic(record: dict[str, Any]) -> dict[str, Any]:
    request, response = _section(record, "request"), _section(record, "response")
    messages = request.get("messages")
    contexts: list[Any] = []
    if isinstance(messages, list):
        for message in messages:
            if not isinstance(message, dict) or not isinstance(message.get("content"), list):
                continue
            for block in message["content"]:
                if not isinstance(block, dict):
                    continue
                kind = block.get("type")
                if kind == "tool_result":
                    text = _blocks_text(block.get("content")) or _text(block.get("content"))
                    if text:
                        contexts.append({"id": block.get("tool_use_id"), "text": text})
                elif kind == "document":
                    source = _section(block, "source")
                    data = source.get("data")
                    text = data if isinstance(data, str) else _text(source.get("content"))
                    if text:
                        contexts.append({"id": block.get("title") or f"doc-{len(contexts)}", "text": text})
                elif kind == "search_result":
                    text = _blocks_text(block.get("content"))
                    if text:
                        contexts.append({"id": block.get("source") or block.get("title"), "text": text})
    question = _last_message(messages, "user")
    question, tagged = _split_tagged_context(question)
    contexts.extend(tagged)
    answer = _blocks_text(response.get("content"))
    cited: list[str] = []
    for block in response.get("content") or []:
        for citation in (block.get("citations") or []) if isinstance(block, dict) else []:
            if isinstance(citation, dict):
                name = citation.get("document_title") or citation.get("source")
                if name is None and isinstance(citation.get("document_index"), int):
                    index = citation["document_index"]
                    if 0 <= index < len(contexts) and isinstance(contexts[index], dict):
                        name = contexts[index].get("id")
                if name:
                    cited.append(str(name))
    return _clean(
        {
            "id": record.get("id") or response.get("id"),
            "question": question,
            "answer": answer,
            "contexts": contexts,
            "citation_ids": list(dict.fromkeys(cited)),
            "latency_ms": _number(record.get("latency_ms")),
            "cost_usd": _number(record.get("cost_usd")),
        }
    )


CONVERTERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "langfuse": from_langfuse,
    "openai": from_openai,
    "anthropic": from_anthropic,
}
