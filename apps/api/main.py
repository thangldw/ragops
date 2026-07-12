from __future__ import annotations

import hmac
import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ragops import __version__
from ragops.engine import compare, evaluate
from ragops.loader import ContractError, responses_from_data, scenario_from_dict
from ragops.store import ExperimentStore

app = FastAPI(title="RAGOps API", version=__version__)


class EvaluateRequest(BaseModel):
    scenario: dict
    responses: list[dict]


class CompareRequest(BaseModel):
    scenario: dict
    baseline: list[dict]
    candidate: list[dict]


class ReviewRequest(BaseModel):
    status: str
    reviewer: str
    note: str = ""


def configured_store() -> ExperimentStore:
    path = os.getenv("RAGOPS_STORE")
    if not path:
        raise HTTPException(status_code=503, detail="RAGOPS_STORE is not configured")
    return ExperimentStore(path)


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = os.getenv("RAGOPS_API_KEY")
    if expected and (x_api_key is None or not hmac.compare_digest(x_api_key, expected)):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(Path(__file__).parents[1] / "web" / "index.html")


@app.post("/v1/evaluate", dependencies=[Depends(require_api_key)])
def evaluate_endpoint(payload: EvaluateRequest) -> dict:
    try:
        scenario = scenario_from_dict(payload.scenario)
        responses = responses_from_data(payload.responses)
        return evaluate(scenario, responses).to_dict()
    except (ContractError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/v1/compare", dependencies=[Depends(require_api_key)])
def compare_endpoint(payload: CompareRequest) -> dict:
    try:
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
