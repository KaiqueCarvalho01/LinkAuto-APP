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
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response


def test_multi_role_profile_updates_keep_other_profile_intact():
    _register_user("multirole@example.com", ["ALUNO", "INSTRUTOR"])
    login_response = _login("multirole@example.com")
    headers = {"Authorization": f"Bearer {login_response.json()['data']['access_token']}"}

    first_patch = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={
            "student_profile": {
                "full_name": "Aluno Multi Role",
                "license_type": "B",
            },
            "instructor_profile": {
                "full_name": "Instrutor Multi Role",
                "bio": "Especialista em direção defensiva",
            },
        },
    )
    assert first_patch.status_code == 200

    second_patch = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={"student_profile": {"city": "Mogi Mirim"}},
    )
    assert second_patch.status_code == 200

    me_response = client.get("/api/v1/users/me", headers=headers)
    assert me_response.status_code == 200
    data = me_response.json()["data"]
    assert data["student_profile"]["city"] == "Mogi Mirim"
    assert data["instructor_profile"]["bio"] == "Especialista em direção defensiva"


def test_non_approved_instructor_hidden_from_public_list_until_admin_approval():
    instructor = _register_user("hidden-instructor@example.com", ["INSTRUTOR"])
    _register_user("admin@example.com", ["ADMIN"])

    admin_login = _login("admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['data']['access_token']}"}

    pending_list = client.get("/api/v1/admin/instructors?status=PENDENTE", headers=admin_headers)
    assert pending_list.status_code == 200
    pending_ids = [item["id"] for item in pending_list.json()["data"]]
    assert instructor["id"] in pending_ids

    public_before = client.get("/api/v1/users/public-instructors")
    assert public_before.status_code == 200
    public_before_ids = [item["id"] for item in public_before.json()["data"]]
    assert instructor["id"] not in public_before_ids

    approve = client.patch(
        f"/api/v1/admin/instructors/{instructor['id']}/approve",
        headers=admin_headers,
    )
    assert approve.status_code == 200

    public_after = client.get("/api/v1/users/public-instructors")
    assert public_after.status_code == 200
    public_after_ids = [item["id"] for item in public_after.json()["data"]]
    assert instructor["id"] in public_after_ids
