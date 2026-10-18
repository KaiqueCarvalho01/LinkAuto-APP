"""The name given at registration is stored on the new profiles (#87)."""

from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def _register(client: TestClient, **body: object) -> dict[str, Any]:
    return client.post(
        "/api/v1/auth/register",
        json={"email": "nome@test.com", "password": "Pass1234!", **body},
    ).json()


def test_name_is_stored_on_every_created_profile(client: TestClient) -> None:
    data = _register(client, roles=["ALUNO", "INSTRUTOR"], full_name="  Ana Souza ")["data"]

    assert data["student_profile"]["full_name"] == "Ana Souza"
    assert data["instructor_profile"]["full_name"] == "Ana Souza"
    # A named profile gets a name-based public slug right away (#72)
    assert data["student_profile"]["slug"].startswith("ana-souza-")


@pytest.mark.parametrize("full_name", [None, "", "   "])
def test_name_is_optional(client: TestClient, full_name: str | None) -> None:
    data = _register(client, roles=["ALUNO"], full_name=full_name)["data"]

    assert data["student_profile"]["full_name"] is None
    assert data["student_profile"]["slug"].startswith("aluno-")


def test_name_is_at_most_255_characters(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "longo@test.com",
            "password": "Pass1234!",
            "roles": ["ALUNO"],
            "full_name": "x" * 256,
        },
    )

    assert resp.status_code == 422
