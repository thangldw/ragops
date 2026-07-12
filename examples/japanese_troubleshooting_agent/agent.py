from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str
    roles: tuple[str, ...]
    entities: tuple[str, ...]
    authority: int


@dataclass(frozen=True)
class SearchHit:
    document: Document
    lexical_score: float
    graph_score: float

    @property
    def score(self) -> float:
        return self.lexical_score + self.graph_score + self.document.authority * 0.01


@dataclass(frozen=True)
class AgentResult:
    answer: str
    citation_ids: tuple[str, ...]
    retrieved_ids: tuple[str, ...]
    decision: str
    latency_ms: int
    metadata: dict[str, Any]


class TroubleshootingAgent:
    """Deterministic GraphRAG-style reference application.

    It demonstrates product boundaries and trace integration without claiming
    model intelligence. ACL filtering happens before lexical/graph ranking.
    """

    def __init__(
        self, data_dir: str | Path | None = None, *, graph_enabled: bool = True
    ) -> None:
        root = Path(data_dir) if data_dir else Path(__file__).parent / "data"
        document_data = json.loads((root / "documents.json").read_text(encoding="utf-8"))
        self.documents = tuple(
            Document(
                id=item["id"],
                title=item["title"],
                text=item["text"],
                roles=tuple(item["roles"]),
                entities=tuple(item["entities"]),
                authority=item["authority"],
            )
            for item in document_data
        )
        self.graph: dict[str, tuple[str, ...]] = {
            node: tuple(neighbors)
            for node, neighbors in json.loads(
                (root / "graph.json").read_text(encoding="utf-8")
            ).items()
        }
        self.graph_enabled = graph_enabled

    def ask(self, question: str, *, role: str = "engineer", top_k: int = 3) -> AgentResult:
        started = time.perf_counter()
        hits = self.retrieve(question, role=role, top_k=top_k)
        if not hits:
            answer = "Machine model and site must be confirmed before providing a procedure."
            decision = "clarify"
            citations: tuple[str, ...] = ()
        else:
            selected = self._select_evidence(question, hits)
            answer = " ".join(hit.document.text for hit in selected)
            citations = tuple(hit.document.id for hit in selected)
            decision = self._decision(question)
        elapsed = max(1, int((time.perf_counter() - started) * 1000))
        return AgentResult(
            answer=answer,
            citation_ids=citations,
            retrieved_ids=tuple(hit.document.id for hit in hits),
            decision=decision,
            latency_ms=elapsed,
            metadata={
                "application": "jp-troubleshooting-reference-agent",
                "build": "offline-v1",
                "retriever": (
                    "lexical-graph-acl-v1" if self.graph_enabled else "lexical-acl-baseline-v1"
                ),
                "generator": "deterministic-evidence-composer-v1",
                "role": role,
            },
        )

    def retrieve(self, question: str, *, role: str, top_k: int = 3) -> tuple[SearchHit, ...]:
        query_tokens = _tokens(question)
        query_entities = self._query_entities(question) if self.graph_enabled else set()
        expanded = query_entities | {
            neighbor for entity in query_entities for neighbor in self.graph.get(entity, ())
        }
        hits: list[SearchHit] = []
        for document in self.documents:
            if role not in document.roles:
                continue
            document_tokens = _tokens(f"{document.title} {document.text}")
            lexical = len(query_tokens & document_tokens) / max(1, len(query_tokens))
            graph_overlap = len(set(document.entities) & expanded)
            graph_score = min(0.6, graph_overlap * 0.2)
            intent_bonus = self._intent_bonus(question, document)
            if lexical > 0 or graph_score > 0:
                hits.append(SearchHit(document, lexical + intent_bonus, graph_score))
        hits.sort(key=lambda hit: (-hit.score, hit.document.id))
        return tuple(hits[:top_k])

    def trace(self, case_id: str, question: str, *, role: str = "engineer") -> dict[str, Any]:
        result = self.ask(question, role=role)
        return {
            "schema_version": "0.4",
            "case_id": case_id,
            "input": {"question": question, "role": role},
            "output": {
                "answer": result.answer,
                "citation_ids": list(result.citation_ids),
                "decision": result.decision,
            },
            "retrieval": {"document_ids": list(result.retrieved_ids)},
            "latency_ms": result.latency_ms,
            "usage": {"cost_usd": 0.0},
            "human_approved": False,
            "metadata": result.metadata,
        }

    def _query_entities(self, question: str) -> set[str]:
        normalized = question.casefold()
        entities = {node for node in self.graph if node.casefold() in normalized}
        aliases = {
            "エスカレーション": "EscalationPolicy",
            "メール": "ExternalAction",
            "送信": "HumanApproval",
            "承認": "HumanApproval",
        }
        entities.update(entity for term, entity in aliases.items() if term in question)
        return entities

    @staticmethod
    def _intent_bonus(question: str, document: Document) -> float:
        normalized = question.casefold()
        title = document.title.casefold()
        bonus = 0.0
        if "エスカレーション" in normalized and "escalation" in title:
            bonus += 0.8
        if "メール" in normalized and "communication" in title:
            bonus += 0.8
        if "一次対応" in normalized and "manual" in title:
            bonus += 0.4
        if "条件" in normalized and "policy" in title:
            bonus += 0.3
        return bonus

    @staticmethod
    def _decision(question: str) -> str:
        normalized = question.casefold()
        if any(marker in normalized for marker in ("送信", "作成", "削除", "send", "create")):
            return "request_approval"
        if "エスカレーション" in normalized or "escalat" in normalized:
            return "escalate"
        return "answer"

    @staticmethod
    def _select_evidence(question: str, hits: tuple[SearchHit, ...]) -> tuple[SearchHit, ...]:
        normalized = question.casefold()
        wants_synthesis = any(term in normalized for term in ("まとめ", " and ", "踏まえ"))
        if not wants_synthesis or len(hits) < 2:
            return hits[:1]
        first = hits[0]
        if "条件" in normalized:
            policy = next(
                (hit for hit in hits[1:] if "policy" in hit.document.title.casefold()),
                hits[1],
            )
            return (first, policy)
        return hits[:2]


def result_as_dict(result: AgentResult) -> dict[str, Any]:
    return asdict(result)


def _tokens(value: str) -> set[str]:
    latin = re.findall(r"[a-zA-Z0-9\-]+", value.casefold())
    japanese = re.findall(r"[一-龯ぁ-んァ-ン]{2,}", value)
    return set(latin + japanese)
