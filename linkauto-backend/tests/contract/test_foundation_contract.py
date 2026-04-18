from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_ping_returns_standard_success_envelope():
    response = client.get("/api/v1/foundation/ping")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == {"data", "error", "meta"}
    assert payload["error"] is None
    assert payload["data"]["message"] == "foundation_ok"


def test_login_returns_auth_envelope_and_refresh_cookie():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "student@example.com", "password": "strong-password"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["error"] is None
    assert "access_token" in payload["data"]
    assert payload["data"]["token_type"] == "bearer"
    set_cookie = response.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "Secure" in set_cookie
    assert "SameSite=strict" in set_cookie


def test_conflict_returns_standard_error_envelope():
    response = client.post("/api/v1/foundation/conflict")

    assert response.status_code == 409
    payload = response.json()
    assert payload["data"] is None
    assert payload["error"]["code"] == "CONFLICT"
    assert "First-write-wins" in payload["error"]["message"]


def test_protected_endpoint_requires_bearer_token():
    response = client.get("/api/v1/foundation/protected")

    assert response.status_code == 401
    payload = response.json()
    assert payload["data"] is None
    assert payload["error"]["code"] == "UNAUTHORIZED"
