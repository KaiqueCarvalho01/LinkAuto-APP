"""Profiles get a stored public slug when created, and it stays stable (#72)."""

from typing import TYPE_CHECKING

from app.models import InstructorProfile, StudentProfile

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session


def _register(client: TestClient, email: str, roles: list[str]) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register", json={"email": email, "password": "Pass1234!", "roles": roles}
    )
    token = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "Pass1234!"}
    ).json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_registration_stores_slugs_and_me_returns_them(
    client: TestClient, db_session: Session
) -> None:
    headers = _register(client, "both@test.com", ["ALUNO", "INSTRUTOR"])

    me = client.get("/api/v1/users/me", headers=headers).json()["data"]

    student = db_session.get(StudentProfile, me["id"])
    instructor = db_session.get(InstructorProfile, me["id"])
    assert student is not None
    assert instructor is not None
    # Stored at registration, before any public page was ever requested
    assert me["student_profile"]["slug"] == student.slug
    assert me["instructor_profile"]["slug"] == instructor.slug
    assert student.slug.startswith("aluno-")
    assert instructor.slug.startswith("instrutor-")


def test_student_public_profile_is_reachable_by_its_slug(client: TestClient) -> None:
    headers = _register(client, "ana@test.com", ["ALUNO"])
    client.patch(
        "/api/v1/users/me",
        json={"student_profile": {"full_name": "Ana Souza", "city": "Campinas"}},
        headers=headers,
    )
    slug = client.get("/api/v1/users/me", headers=headers).json()["data"]["student_profile"]["slug"]

    resp = client.get(f"/api/v1/students/{slug}/public")

    assert slug.startswith("ana-souza-campinas-")
    assert resp.status_code == 200


def test_slug_gets_a_name_once_then_stays(client: TestClient) -> None:
    headers = _register(client, "bia@test.com", ["ALUNO"])

    def slug() -> str:
        return client.get("/api/v1/users/me", headers=headers).json()["data"]["student_profile"][
            "slug"
        ]

    placeholder = slug()
    client.patch(
        "/api/v1/users/me", json={"student_profile": {"full_name": "Bia"}}, headers=headers
    )
    named = slug()
    client.patch(
        "/api/v1/users/me", json={"student_profile": {"full_name": "Beatriz"}}, headers=headers
    )

    assert placeholder.startswith("aluno-")
    assert named.startswith("bia-")
    # Renaming doesn't break links that were already shared
    assert slug() == named
