from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

FRONTEND_ORIGIN = "http://localhost:5173"


def test_health_returns_ok():
    response = client.get("/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == app.version


def test_openapi_lists_v1_health():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/v1/health" in response.json()["paths"]


def test_cors_allows_frontend_origin():
    response = client.get("/v1/health", headers={"Origin": FRONTEND_ORIGIN})

    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN
