from fastapi import APIRouter
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
