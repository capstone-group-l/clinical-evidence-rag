import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Allow the frontend to call the API from the browser.
cors_origins = (
    os.getenv("CORS_ORIGINS", "http://localhost:5173")
    .replace(" ", "")
    .split(",")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
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
