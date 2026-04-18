from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def _register_user(email: str, roles: list[str], password: str = "strong-password") -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "roles": roles},
    )
    assert response.status_code == 201
    return response.json()["data"]


def _login(email: str, password: str = "strong-password"):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def test_auth_register_login_refresh_and_reset_contract():
    _register_user("contract-user@example.com", ["ALUNO"])

    login_response = _login("contract-user@example.com")
    assert login_response.status_code == 200
    login_payload = login_response.json()
    assert set(login_payload.keys()) == {"data", "error", "meta"}
    assert login_payload["error"] is None
    assert login_payload["data"]["token_type"] == "bearer"
    assert isinstance(login_payload["data"]["access_token"], str)

    set_cookie = login_response.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "Secure" in set_cookie
    assert "SameSite=strict" in set_cookie

    refresh_cookie_value = set_cookie.split("refresh_token=", 1)[1].split(";", 1)[0]
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": refresh_cookie_value},
    )
    assert refresh_response.status_code == 200
    refresh_payload = refresh_response.json()
    assert refresh_payload["error"] is None
    assert isinstance(refresh_payload["data"]["access_token"], str)
    assert refresh_payload["data"]["token_type"] == "bearer"

    missing_cookie_response = client.post("/api/v1/auth/refresh")
    assert missing_cookie_response.status_code == 401
    assert missing_cookie_response.json()["error"]["code"] == "UNAUTHORIZED"

    reset_response = client.post(
        "/api/v1/auth/password-reset",
        json={"email": "contract-user@example.com"},
    )
    assert reset_response.status_code == 202
    reset_payload = reset_response.json()
    assert reset_payload["error"] is None
    assert reset_payload["data"]["status"] == "accepted"


def test_users_me_get_and_patch_contract():
    _register_user("profile-contract@example.com", ["ALUNO", "INSTRUTOR"])
    login_response = _login("profile-contract@example.com")
    access_token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    me_response = client.get("/api/v1/users/me", headers=headers)
    assert me_response.status_code == 200
    me_payload = me_response.json()
    assert me_payload["error"] is None
    assert me_payload["data"]["email"] == "profile-contract@example.com"
    assert sorted(me_payload["data"]["roles"]) == ["ALUNO", "INSTRUTOR"]

    patch_response = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={
            "student_profile": {"full_name": "Aluno Contrato", "city": "Mogi Mirim"},
            "instructor_profile": {"full_name": "Instrutor Contrato", "city": "Mogi Mirim"},
        },
    )
    assert patch_response.status_code == 200
    patch_payload = patch_response.json()
    assert patch_payload["error"] is None
    assert patch_payload["data"]["student_profile"]["full_name"] == "Aluno Contrato"
    assert patch_payload["data"]["instructor_profile"]["full_name"] == "Instrutor Contrato"
