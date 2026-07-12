from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ragops.models import EvalCase, RecordedResponse, RedTeamPolicy, Scenario, Thresholds


class ContractError(ValueError):
    """Raised when a scenario or response file violates the v0.1 contract."""


def _read_json(path: str | Path) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"Cannot load JSON from {path}: {exc}") from exc


def load_scenario(path: str | Path) -> Scenario:
    return scenario_from_dict(_read_json(path))


def scenario_from_dict(data: dict[str, Any]) -> Scenario:
    try:
        thresholds = Thresholds(**data["thresholds"])
        redteam = RedTeamPolicy(
            forbidden_output_terms=tuple(data.get("redteam", {}).get("forbidden_output_terms", [])),
            require_human_approval_for_external_actions=data.get("redteam", {}).get(
                "require_human_approval_for_external_actions", True
            ),
            external_action_markers=tuple(
                data.get("redteam", {}).get(
                    "external_action_markers", ["sent email", "created ticket", "deleted"]
                )
            ),
        )
        cases = tuple(
            EvalCase(
                id=item["id"],
                question=item["question"],
                evidence=tuple(item["evidence"]),
                required_citation_ids=tuple(item["required_citation_ids"]),
            )
            for item in data["cases"]
        )
        scenario = Scenario(
            schema_version=data["schema_version"],
            id=data["id"],
            name=data["name"],
            thresholds=thresholds,
            redteam=redteam,
            cases=cases,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ContractError(f"Invalid scenario contract: {exc}") from exc

    if scenario.schema_version != "0.1":
        raise ContractError(f"Unsupported scenario schema: {scenario.schema_version}")
    if not scenario.cases or len({case.id for case in scenario.cases}) != len(scenario.cases):
        raise ContractError("Scenario needs at least one case and case IDs must be unique")
    return scenario


def load_responses(path: str | Path) -> tuple[RecordedResponse, ...]:
    return responses_from_data(_read_json(path))


def responses_from_data(data: list[dict[str, Any]]) -> tuple[RecordedResponse, ...]:
    try:
        responses = tuple(
            RecordedResponse(
                case_id=item["case_id"],
                answer=item["answer"],
                citation_ids=tuple(item.get("citation_ids", [])),
                latency_ms=item["latency_ms"],
                cost_usd=item["cost_usd"],
                human_approved=item.get("human_approved", False),
                retrieved_ids=tuple(item.get("retrieved_ids", [])),
            )
            for item in data
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ContractError(f"Invalid response contract: {exc}") from exc
    if len({response.case_id for response in responses}) != len(responses):
        raise ContractError("Response case IDs must be unique")
    return responses
