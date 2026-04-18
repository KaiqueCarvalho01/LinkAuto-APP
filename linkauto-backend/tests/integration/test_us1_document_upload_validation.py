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


def test_document_upload_rejects_invalid_mime_type():
    instructor = _register_user("doc-invalid-mime@example.com", ["INSTRUTOR"])
    login = _login("doc-invalid-mime@example.com")
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    response = client.post(
        f"/api/v1/instructors/{instructor['id']}/documents",
        headers=headers,
        files={
            "detran_credential": ("credential.txt", b"invalid", "text/plain"),
            "criminal_record": ("record.pdf", b"%PDF-1.4\nsample", "application/pdf"),
        },
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_document_upload_rejects_file_over_10mb():
    instructor = _register_user("doc-oversize@example.com", ["INSTRUTOR"])
    login = _login("doc-oversize@example.com")
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}
    oversized_content = b"a" * (10 * 1024 * 1024 + 1)

    response = client.post(
        f"/api/v1/instructors/{instructor['id']}/documents",
        headers=headers,
        files={
            "detran_credential": ("credential.pdf", oversized_content, "application/pdf"),
            "criminal_record": ("record.pdf", b"%PDF-1.4\nsample", "application/pdf"),
        },
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"


def test_document_upload_accepts_allowed_mime_within_limit():
    instructor = _register_user("doc-valid@example.com", ["INSTRUTOR"])
    login = _login("doc-valid@example.com")
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

    response = client.post(
        f"/api/v1/instructors/{instructor['id']}/documents",
        headers=headers,
        files={
            "detran_credential": ("credential.pdf", b"%PDF-1.4\nsample", "application/pdf"),
            "criminal_record": ("record.png", b"\x89PNG\r\n\x1a\nsample", "image/png"),
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["error"] is None
    assert payload["data"]["instructor_id"] == instructor["id"]
