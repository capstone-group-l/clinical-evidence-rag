from fastapi import APIRouter

from app.api.v1.endpoints import health, query, users

api_router = APIRouter()

# Register routes
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(query.router, tags=["Query"])
api_router.include_router(users.router, tags=["Users"])
