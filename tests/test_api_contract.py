import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

from fastapi import HTTPException

from apps.api.main import (
    EvaluatorDriftRequest,
    StatisticalCompareRequest,
    _positive_env_int,
    _validate_collection_limits,
    _validate_replay_limits,
    evaluator_drift_endpoint,
    require_api_key,
    sequential_compare_endpoint,
    statistical_compare_endpoint,
)


def test_api_auth_fails_closed_when_unconfigured(monkeypatch) -> None:
    monkeypatch.delenv("RAGOPS_API_KEY", raising=False)
    monkeypatch.delenv("RAGOPS_INSECURE_DEV_MODE", raising=False)

    with pytest.raises(HTTPException) as captured:
        require_api_key(None)

    assert captured.value.status_code == 503


def test_api_auth_accepts_only_matching_configured_key(monkeypatch) -> None:
    monkeypatch.setenv("RAGOPS_API_KEY", "expected-key")
    monkeypatch.delenv("RAGOPS_INSECURE_DEV_MODE", raising=False)

    with pytest.raises(HTTPException) as captured:
        require_api_key("wrong-key")
    assert captured.value.status_code == 401

    require_api_key("expected-key")


def test_insecure_dev_mode_is_explicit_and_conflicts_with_key(monkeypatch) -> None:
    monkeypatch.delenv("RAGOPS_API_KEY", raising=False)
    monkeypatch.setenv("RAGOPS_INSECURE_DEV_MODE", "true")
    require_api_key(None)

    monkeypatch.setenv("RAGOPS_API_KEY", "configured")
    with pytest.raises(HTTPException) as captured:
        require_api_key("configured")
    assert captured.value.status_code == 503


def test_collection_limit_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("RAGOPS_MAX_CASES", "1")
    scenario = {"cases": [{"id": "one"}, {"id": "two"}]}

    with pytest.raises(HTTPException) as captured:
        _validate_collection_limits(scenario, [])

    assert captured.value.status_code == 413


@pytest.mark.parametrize("value", ["0", "-1", "many"])
def test_invalid_limit_configuration_returns_service_error(monkeypatch, value: str) -> None:
    monkeypatch.setenv("RAGOPS_MAX_CASES", value)

    with pytest.raises(HTTPException) as captured:
        _positive_env_int("RAGOPS_MAX_CASES", 1000)

    assert captured.value.status_code == 503


def test_compose_is_localhost_bound_and_requires_key() -> None:
    compose = Path("compose.yaml").read_text(encoding="utf-8")

    assert '"127.0.0.1:8000:8000"' in compose
    assert "RAGOPS_API_KEY:?" in compose
    assert "RAGOPS_API_KEY:-" not in compose


def _bundle(name: str) -> dict:
    return json.loads(
        Path(f"scenarios/statistical_gate/{name}.json").read_text(encoding="utf-8")
    )


def _fixed_policy() -> dict:
    return {
        "confidence": 0.95,
        "minimum_cases": 3,
        "resamples": 200,
        "seed": 42,
        "metrics": {
            "citation_precision": {
                "direction": "higher",
                "minimum": 0.9,
                "max_regression": 0.03,
            }
        },
    }


def test_statistical_and_sequential_api_adapters() -> None:
    fixed = statistical_compare_endpoint(
        StatisticalCompareRequest(
            baseline=_bundle("baseline"),
            candidate=_bundle("candidate-pass"),
            policy=_fixed_policy(),
        )
    )
    sequential_policy = {
        **_fixed_policy(),
        "minimum_repeats": 2,
        "maximum_repeats": 2,
        "look_every": 1,
    }
    sequential = sequential_compare_endpoint(
        StatisticalCompareRequest(
            baseline=_bundle("baseline"),
            candidate=_bundle("candidate-pass"),
            policy=sequential_policy,
        )
    )

    assert fixed["passed"] is True
    assert sequential["decision"] == "pass"


def test_evaluator_drift_api_requires_frozen_evidence() -> None:
    reference = _bundle("baseline")
    current = json.loads(json.dumps(reference))
    current["provenance"]["evaluator"] = "citation-precision-v2"
    current["records"] = [
        {
            **record,
            "metrics": {"citation_precision": record["metrics"]["citation_precision"] + 0.005},
        }
        for record in current["records"]
    ]
    report = evaluator_drift_endpoint(
        EvaluatorDriftRequest(
            reference=reference,
            current=current,
            policy={
                "confidence": 0.95,
                "minimum_cases": 3,
                "resamples": 200,
                "seed": 42,
                "metrics": {"citation_precision": {"max_absolute_change": 0.02}},
            },
        )
    )

    assert report["passed"] is True


def test_replay_api_observation_limit_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("RAGOPS_MAX_REPLAY_OBSERVATIONS", "1")

    with pytest.raises(HTTPException) as captured:
        _validate_replay_limits(_bundle("baseline"))

    assert captured.value.status_code == 413
