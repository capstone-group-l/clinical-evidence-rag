import psycopg
from fastapi import APIRouter, Depends, Query
from psycopg.rows import dict_row

from app.auth import get_current_user, require_admin
from app.config import Settings
from app.schemas import UserOut, UserPage

router = APIRouter()

PAGE_SIZE = 25


def list_users(page: int) -> tuple[list[dict], int]:
    settings = Settings()
    offset = (page - 1) * PAGE_SIZE
    with psycopg.connect(settings.database_url, row_factory=dict_row) as conn:
        total = conn.execute("SELECT count(*) AS n FROM users").fetchone()["n"]
        rows = conn.execute(
            "SELECT user_id::text AS user_id, email, role, status "
            "FROM users ORDER BY created_at LIMIT %s OFFSET %s",
            (PAGE_SIZE, offset),
        ).fetchall()
    return rows, total


@router.get("/me", response_model=UserOut, summary="Get My Profile")
def get_me(user: dict = Depends(get_current_user)) -> dict:
    return user


@router.get("/admin/users", response_model=UserPage, summary="List All Users")
def get_all_users(
    page: int = Query(1, ge=1),
    admin: dict = Depends(require_admin),
) -> dict:
    rows, total = list_users(page)
    return {
        "users": rows,
        "total": total,
        "page": page,
        "page_size": PAGE_SIZE,
    }
