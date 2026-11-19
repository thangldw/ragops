"""Small helpers shared by the ``ragops`` command handlers."""

from __future__ import annotations

import shlex
from collections.abc import Callable

from ragops.loader import ContractError
from ragops.plugins import (
    AbstentionContractEvaluator,
    AnswerLengthBudgetEvaluator,
    CaseEvaluator,
    CitationCorrectnessEvaluator,
    ClaimSupportEvaluator,
    RetrievalRecallEvaluator,
    SourceFreshnessEvaluator,
    StrictGroundingEvaluator,
)
from ragops.semantic import CommandSemanticScorer, SemanticGroundingEvaluator


def _named_csv_values(values: list[str], label: str) -> dict[str, tuple[str, ...]]:
    result = {}
    for value in values:
        if "=" not in value:
            raise ContractError(f"{label} must use NAME=VALUE,VALUE")
        name, raw_items = value.split("=", 1)
        items = tuple(item for item in raw_items.split(",") if item)
        if not name or not items or name in result:
            raise ContractError(f"{label} names must be non-empty and unique")
        result[name] = items
    return result


def _named_int_values(values: list[str], label: str) -> dict[str, int]:
    result = {}
    for value in values:
        if "=" not in value:
            raise ContractError(f"{label} must use SELECTOR=COUNT")
        selector, raw_count = value.rsplit("=", 1)
        try:
            count = int(raw_count)
        except ValueError as exc:
            raise ContractError(f"{label} count must be an integer") from exc
        if not selector or selector in result or count <= 0:
            raise ContractError(f"{label} selectors must be non-empty, unique, and positive")
        result[selector] = count
    return result


def _evaluators_from_names(
    names: list[str],
    *,
    answer_length_limit: int = 500,
    semantic_command: str | None = None,
) -> tuple[CaseEvaluator, ...]:
    factories: dict[str, Callable[[], CaseEvaluator]] = {
        "retrieval_recall": RetrievalRecallEvaluator,
        "citation_correctness": CitationCorrectnessEvaluator,
        "claim_support": ClaimSupportEvaluator,
        "strict_grounding": StrictGroundingEvaluator,
        "semantic_grounding": lambda: SemanticGroundingEvaluator(
            CommandSemanticScorer(_semantic_command(semantic_command))
        ),
        "answer_length_budget": lambda: AnswerLengthBudgetEvaluator(
            max_characters=answer_length_limit
        ),
        "source_freshness": SourceFreshnessEvaluator,
        "abstention_contract": AbstentionContractEvaluator,
    }
    return tuple(factories[name]() for name in names)


def _semantic_command(value: str | None) -> tuple[str, ...]:
    if not value:
        raise SystemExit("semantic_grounding requires --semantic-command")
    return tuple(shlex.split(value))
