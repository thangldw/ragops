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

app = FastAPI(title="RAGOps API", version=__version__)


class EvaluateRequest(BaseModel):
    scenario: dict
    responses: list[dict]


class CompareRequest(BaseModel):
    scenario: dict
    baseline: list[dict]
    candidate: list[dict]


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
