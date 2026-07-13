from pathlib import Path

import pytest

pytest.importorskip("fastapi")

from fastapi import HTTPException

from apps.api.main import _positive_env_int, _validate_collection_limits, require_api_key


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
