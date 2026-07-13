from __future__ import annotations

import hmac
import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from ragops import __version__
from ragops.control_plane import ControlPlane
from ragops.engine import compare, evaluate
from ragops.loader import ContractError, responses_from_data, scenario_from_dict
from ragops.store import ExperimentStore

app = FastAPI(title="RAGOps API", version=__version__)

DEFAULT_MAX_REQUEST_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_CASES = 1000


class EvaluateRequest(BaseModel):
    scenario: dict
    responses: list[dict]


class SavedEvaluateRequest(EvaluateRequest):
    label: str = ""


class CompareRequest(BaseModel):
    scenario: dict
    baseline: list[dict]
    candidate: list[dict]


class ReviewRequest(BaseModel):
    status: str
    reviewer: str
    note: str = ""


def configured_store(
    x_workspace_id: str | None = Header(default=None),
    x_workspace_key: str | None = Header(default=None),
) -> ExperimentStore:
    control_root = os.getenv("RAGOPS_CONTROL_PLANE")
    if control_root:
        if not x_workspace_id or not x_workspace_key:
            raise HTTPException(status_code=401, detail="Workspace credentials are required")
        try:
            return ControlPlane(control_root).workspace_store(x_workspace_id, x_workspace_key)
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
    path = os.getenv("RAGOPS_STORE")
    if not path:
        raise HTTPException(status_code=503, detail="RAGOPS_STORE is not configured")
    return ExperimentStore(path)


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = os.getenv("RAGOPS_API_KEY", "").strip()
    insecure_dev_mode = os.getenv("RAGOPS_INSECURE_DEV_MODE", "").casefold() == "true"
    if expected and insecure_dev_mode:
        raise HTTPException(
            status_code=503,
            detail="RAGOPS_API_KEY and RAGOPS_INSECURE_DEV_MODE cannot both be enabled",
        )
    if insecure_dev_mode:
        return
    if not expected:
        raise HTTPException(
            status_code=503,
            detail=(
                "API authentication is not configured; set RAGOPS_API_KEY or explicitly "
                "enable RAGOPS_INSECURE_DEV_MODE=true for local development"
            ),
        )
    if x_api_key is None or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.middleware("http")
async def enforce_request_size(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH"}:
        maximum = _positive_env_int("RAGOPS_MAX_REQUEST_BYTES", DEFAULT_MAX_REQUEST_BYTES)
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                declared = int(content_length)
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length"})
            if declared > maximum:
                return JSONResponse(status_code=413, content={"detail": "Request body is too large"})
        body = await request.body()
        if len(body) > maximum:
            return JSONResponse(status_code=413, content={"detail": "Request body is too large"})
    return await call_next(request)


def _positive_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=f"{name} must be a positive integer") from exc
    if value <= 0:
        raise HTTPException(status_code=503, detail=f"{name} must be a positive integer")
    return value


def _validate_collection_limits(scenario: dict, *response_sets: list[dict]) -> None:
    maximum = _positive_env_int("RAGOPS_MAX_CASES", DEFAULT_MAX_CASES)
    cases = scenario.get("cases", [])
    if not isinstance(cases, list):
        return
    if len(cases) > maximum or any(len(responses) > maximum for responses in response_sets):
        raise HTTPException(
            status_code=413,
            detail=f"Scenario and response collections are limited to {maximum} cases",
        )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(Path(__file__).parents[1] / "web" / "index.html")


@app.post("/v1/evaluate", dependencies=[Depends(require_api_key)])
def evaluate_endpoint(payload: EvaluateRequest) -> dict:
    try:
        _validate_collection_limits(payload.scenario, payload.responses)
        scenario = scenario_from_dict(payload.scenario)
        responses = responses_from_data(payload.responses)
        return evaluate(scenario, responses).to_dict()
    except (ContractError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/compare", dependencies=[Depends(require_api_key)])
def compare_endpoint(payload: CompareRequest) -> dict:
    try:
        _validate_collection_limits(payload.scenario, payload.baseline, payload.candidate)
        scenario = scenario_from_dict(payload.scenario)
        baseline = responses_from_data(payload.baseline)
        candidate = responses_from_data(payload.candidate)
        return compare(scenario, baseline, candidate).to_dict()
    except (ContractError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/runs", dependencies=[Depends(require_api_key)])
def list_runs(limit: int = 20, store: ExperimentStore = Depends(configured_store)) -> list[dict]:
    try:
        return store.list_runs(limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/trends/{scenario_id}/{metric}", dependencies=[Depends(require_api_key)])
def metric_trend(
    scenario_id: str,
    metric: str,
    limit: int = 50,
    store: ExperimentStore = Depends(configured_store),
) -> list[dict]:
    try:
        return store.metric_trend(scenario_id, metric, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/runs/{run_id}/review", dependencies=[Depends(require_api_key)])
def review_run(
    run_id: str,
    payload: ReviewRequest,
    store: ExperimentStore = Depends(configured_store),
) -> dict[str, str]:
    try:
        store.review(
            run_id,
            status=payload.status,
            reviewer=payload.reviewer,
            note=payload.note,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"run_id": run_id, "review_status": payload.status}


@app.post("/v1/runs/evaluate", dependencies=[Depends(require_api_key)])
def evaluate_and_save(
    payload: SavedEvaluateRequest,
    store: ExperimentStore = Depends(configured_store),
) -> dict:
    try:
        _validate_collection_limits(payload.scenario, payload.responses)
        scenario = scenario_from_dict(payload.scenario)
        responses = responses_from_data(payload.responses)
        report = evaluate(scenario, responses)
    except (ContractError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    run_id = store.save(report, label=payload.label)
    return {"run_id": run_id, "report": report.to_dict()}
