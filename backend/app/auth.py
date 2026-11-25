import httpx
import psycopg
from fastapi import Depends, Header, HTTPException
from psycopg.rows import dict_row

from app.config import Settings


# It calls the Supabase Auth API to get the user ID from a token.
def get_supabase_user_id(token: str) -> str | None:
    settings = Settings()
    response = httpx.get(
        f"{settings.supabase_url}/auth/v1/user",
        headers={
            "apikey": settings.supabase_anon_key or "",
            "Authorization": f"Bearer {token}",
        },
    )
    if response.status_code != 200:
        return None
    return response.json()["id"]


# Search for a row by user_id in the database.
def find_user(user_id: str) -> dict | None:
    settings = Settings()
    with psycopg.connect(settings.database_url, row_factory=dict_row) as conn:
        return conn.execute(
            "SELECT user_id::text AS user_id, email, role, status "
            "FROM users WHERE user_id = %s",
            (user_id,),
        ).fetchone()


# Get the current user from the authorization header.
def get_current_user(authorization: str | None = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not logged in")

    token = authorization.removeprefix("Bearer ")
    user_id = get_supabase_user_id(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = find_user(user_id)
    if user is None:
        raise HTTPException(status_code=403, detail="User profile not found")
    if user["status"] != "approved":
        raise HTTPException(status_code=403, detail="Account not approved")
    return user


# It requires admin privalages for certain features.
def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user
