from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ragops.models import EvalCase, Finding, RecordedResponse


@dataclass(frozen=True)
class PluginResult:
    metrics: dict[str, float]
    findings: tuple[Finding, ...] = ()


@runtime_checkable
class CaseEvaluator(Protocol):
    """Stable extension point for deterministic or provider-backed evaluators."""

    name: str

    def evaluate(self, case: EvalCase, response: RecordedResponse) -> PluginResult: ...


class EvaluatorRegistry:
    def __init__(self) -> None:
        self._evaluators: dict[str, CaseEvaluator] = {}

    def register(self, evaluator: CaseEvaluator) -> None:
        if not evaluator.name or evaluator.name in self._evaluators:
            raise ValueError(f"Evaluator name must be unique: {evaluator.name!r}")
        self._evaluators[evaluator.name] = evaluator

    def values(self) -> tuple[CaseEvaluator, ...]:
        return tuple(self._evaluators.values())


class RetrievalRecallEvaluator:
    name = "retrieval_recall"

    def evaluate(self, case: EvalCase, response: RecordedResponse) -> PluginResult:
        relevant = set(case.required_citation_ids)
        if not relevant:
            score = 1.0
        else:
            score = len(relevant.intersection(response.retrieved_ids)) / len(relevant)
        return PluginResult(metrics={"score": score})
