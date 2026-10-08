from fastapi import FastAPI
import math

from app.api.v1.router import api_router

app = FastAPI(
    title="Clinical Decision Support Assistant API",
    description="""
    Backend service providing grounded clinical answers with source validation.
    """,
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Mount all v1 routes under /v1
app.include_router(api_router, prefix="/v1")


@app.get("/", include_in_schema=False)
async def root_redirect():
    return {
        "message": """
        Welcome to the Clinical Decision Support Assistant API. Go
        to /docs for OpenAPI specifications.
        """
    }
