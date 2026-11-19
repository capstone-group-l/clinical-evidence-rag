from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API Health Status",
    description="""
    Returns the operational status of the backend API and current version.
    """,
)
async def get_health() -> HealthResponse:
    return HealthResponse(status="ok", version="1.0.0")


@router.get(
    "/ready",
    summary="Check Pipeline Readiness",
)
async def get_readiness(request: Request):
    ready = getattr(request.app.state, "pipeline_ready", False)
    if ready:
        return JSONResponse(status_code=200, content={"status": "ready"})
    return JSONResponse(status_code=503, content={"status": "loading"})
