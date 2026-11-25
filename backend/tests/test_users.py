import pytest
from app import auth
from app.api.v1.endpoints import users
from app.auth import get_current_user
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

ADMIN = {
    "user_id": "1",
    "email": "admin@example.com",
    "role": "admin",
    "status": "approved",
}
NORMAL = {
    "user_id": "2",
    "email": "user@example.com",
    "role": "user",
    "status": "approved",
}


def log_in_as(user):
    app.dependency_overrides[get_current_user] = lambda: user


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_me_without_token_returns_401():
    response = client.get("/v1/me")
    assert response.status_code == 401


def test_me_returns_my_role():
    log_in_as(NORMAL)
    response = client.get("/v1/me")
    assert response.status_code == 200
    assert response.json()["role"] == "user"


def test_admin_users_blocks_normal_user():
    log_in_as(NORMAL)
    response = client.get("/v1/admin/users")
    assert response.status_code == 403


def test_admin_users_works_for_admin(monkeypatch):
    log_in_as(ADMIN)
    monkeypatch.setattr(users, "list_users", lambda page: ([ADMIN, NORMAL], 2))
    response = client.get("/v1/admin/users")
    assert response.status_code == 200
    body = response.json()
    assert len(body["users"]) == 2
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["page_size"] == 25


def test_admin_users_passes_page(monkeypatch):
    log_in_as(ADMIN)
    seen = {}

    def fake_list(page):
        seen["page"] = page
        return [], 30

    monkeypatch.setattr(users, "list_users", fake_list)
    response = client.get("/v1/admin/users?page=2")
    assert response.status_code == 200
    assert seen["page"] == 2


def test_admin_users_rejects_page_zero():
    log_in_as(ADMIN)
    response = client.get("/v1/admin/users?page=0")
    assert response.status_code == 422


@pytest.mark.parametrize(
    "supabase_id, db_user, expected",
    [
        (None, None, 401),
        ("2", None, 403),
        ("2", {**NORMAL, "status": "pending"}, 403),
        ("2", NORMAL, 200),
    ],
    ids=[
        "invalid_token",
        "missing_profile",
        "unapproved_user",
        "approved_user",
    ],
)
def test_get_current_user_outcomes(
    monkeypatch, supabase_id, db_user, expected
):
    monkeypatch.setattr(
        auth, "get_supabase_user_id", lambda token: supabase_id
    )
    monkeypatch.setattr(auth, "find_user", lambda user_id: db_user)
    response = client.get("/v1/me", headers={"Authorization": "Bearer t"})
    assert response.status_code == expected
