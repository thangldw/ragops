from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from ragops.api.main import app

DEMO = Path("examples/customer_support_demo")
KEY = {"X-API-Key": "test-key"}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture()
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("RAGOPS_API_KEY", "test-key")
    monkeypatch.delenv("RAGOPS_INSECURE_DEV_MODE", raising=False)
    monkeypatch.delenv("RAGOPS_CONTROL_PLANE", raising=False)
    monkeypatch.setenv("RAGOPS_STORE", str(tmp_path / "store.db"))
    return TestClient(app)


def test_health_and_workbench_are_public_with_security_headers(client) -> None:
    assert client.get("/health").status_code == 200
    page = client.get("/")
    assert page.status_code == 200
    assert page.headers["x-content-type-options"] == "nosniff"
    assert client.get("/assets/app.js").status_code == 200


def test_protected_routes_reject_missing_and_wrong_key(client) -> None:
    assert client.get("/v1/runs").status_code == 401
    assert client.get("/v1/runs", headers={"X-API-Key": "nope"}).status_code == 401


def test_evaluate_and_compare_round_trip(client) -> None:
    scenario = _load(DEMO / "scenario.json")
    baseline = _load(DEMO / "output/baseline.json")
    candidate = _load(DEMO / "output/candidate.json")

    evaluated = client.post(
        "/v1/evaluate", headers=KEY, json={"scenario": scenario, "responses": baseline}
    )
    assert evaluated.status_code == 200

    compared = client.post(
        "/v1/compare",
        headers=KEY,
        json={"scenario": scenario, "baseline": baseline, "candidate": candidate},
    )
    assert compared.status_code == 200
    assert compared.json()["passed"] is False


def test_invalid_payload_is_a_422_not_a_crash(client) -> None:
    response = client.post(
        "/v1/evaluate", headers=KEY, json={"scenario": {"bad": 1}, "responses": []}
    )
    assert response.status_code == 422


def test_saved_run_review_and_trend_flow(client) -> None:
    scenario = _load(DEMO / "scenario.json")
    baseline = _load(DEMO / "output/baseline.json")

    saved = client.post(
        "/v1/runs/evaluate",
        headers=KEY,
        json={"scenario": scenario, "responses": baseline, "label": "ci"},
    )
    assert saved.status_code == 200
    run_id = saved.json()["run_id"]

    runs = client.get("/v1/runs", headers=KEY).json()
    assert [run["id"] for run in runs] == [run_id]

    trend = client.get(f"/v1/trends/{scenario['id']}/citation_coverage", headers=KEY)
    assert trend.status_code == 200

    reviewed = client.post(
        f"/v1/runs/{run_id}/review",
        headers=KEY,
        json={"status": "accepted", "reviewer": "qa", "note": "ok"},
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["review_status"] == "accepted"

    missing = client.post(
        "/v1/runs/does-not-exist/review",
        headers=KEY,
        json={"status": "accepted", "reviewer": "qa"},
    )
    assert missing.status_code == 404

    bad_status = client.post(
        f"/v1/runs/{run_id}/review", headers=KEY, json={"status": "bogus", "reviewer": "qa"}
    )
    assert bad_status.status_code == 422


def test_store_routes_need_configuration(client, monkeypatch) -> None:
    monkeypatch.delenv("RAGOPS_STORE", raising=False)
    assert client.get("/v1/runs", headers=KEY).status_code == 503


def test_control_plane_requires_workspace_credentials(client, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("RAGOPS_CONTROL_PLANE", str(tmp_path / "cp"))
    assert client.get("/v1/runs", headers=KEY).status_code == 401
    bad = client.get(
        "/v1/runs", headers={**KEY, "X-Workspace-Id": "w", "X-Workspace-Key": "k"}
    )
    assert bad.status_code == 401


def test_oversized_request_is_rejected(client, monkeypatch) -> None:
    monkeypatch.setenv("RAGOPS_MAX_REQUEST_BYTES", "50")
    response = client.post("/v1/evaluate", headers=KEY, json={"scenario": {"a": "x" * 500}, "responses": []})
    assert response.status_code == 413
