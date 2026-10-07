"""Accounts, profiles, documents and reviews are stored in SQL, not in process memory (#20)."""

from typing import TYPE_CHECKING

from fastapi.testclient import TestClient
from sqlmodel import col, select

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.main import create_app
from app.models import DetranStatus, InstructorDocument, InstructorProfile, StudentProfile, User

if TYPE_CHECKING:
    from sqlmodel import Session


def _fresh_client(db_session: Session) -> TestClient:
    """Build a new app instance (as after a restart, or another worker) on the same DB."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)


def _register(client: TestClient, email: str, roles: list[str]) -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "roles": roles},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


def _login(client: TestClient, email: str) -> dict[str, str]:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['data']['access_token']}"}


def test_registered_user_and_profile_are_stored_in_sql(db_session: Session) -> None:
    user_id = _register(_fresh_client(db_session), "persist@x.com", ["INSTRUTOR", "ALUNO"])

    user = db_session.get(User, user_id)
    assert user is not None
    assert user.email == "persist@x.com"
    assert db_session.get(InstructorProfile, user_id) is not None
    assert db_session.get(StudentProfile, user_id) is not None


def test_login_and_profile_survive_a_restart(db_session: Session) -> None:
    first = _fresh_client(db_session)
    _register(first, "restart@x.com", ["INSTRUTOR"])
    headers = _login(first, "restart@x.com")
    resp = first.patch(
        "/api/v1/users/me",
        headers=headers,
        json={"instructor_profile": {"full_name": "Persistida", "price_per_hour": 75.5}},
    )
    assert resp.status_code == 200

    second = _fresh_client(db_session)
    me = second.get("/api/v1/users/me", headers=_login(second, "restart@x.com"))
    assert me.status_code == 200
    profile = me.json()["data"]["instructor_profile"]
    assert profile["full_name"] == "Persistida"
    assert profile["price_per_hour"] == 75.5


def test_email_is_unique_case_insensitively(db_session: Session) -> None:
    client = _fresh_client(db_session)
    _register(client, "dup@x.com", ["ALUNO"])

    resp = client.post(
        "/api/v1/auth/register",
        json={"email": " DUP@x.com ", "password": "password123", "roles": ["ALUNO"]},
    )
    assert resp.status_code == 400


def test_admin_approval_and_documents_are_persisted(db_session: Session) -> None:
    client = _fresh_client(db_session)
    instructor_id = _register(client, "docs@x.com", ["INSTRUTOR"])
    headers = _login(client, "docs@x.com")
    upload = client.post(
        f"/api/v1/instructors/{instructor_id}/documents",
        headers=headers,
        files={
            "detran_credential": ("c.pdf", b"%PDF-1.4\nx", "application/pdf"),
            "criminal_record": ("r.png", b"\x89PNG\r\n\x1a\nx", "image/png"),
        },
    )
    assert upload.status_code == 201
    stored = db_session.exec(
        select(InstructorDocument).where(col(InstructorDocument.instructor_id) == instructor_id)
    ).all()
    assert len(stored) == 1

    admin = create_access_token("admin-x", settings=get_settings(), roles=["ADMIN"])
    resp = client.patch(
        f"/api/v1/admin/instructors/{instructor_id}/approve",
        headers={"Authorization": f"Bearer {admin}"},
    )
    assert resp.status_code == 200

    profile = db_session.get(InstructorProfile, instructor_id)
    assert profile is not None
    assert profile.detran_status == DetranStatus.APROVADO
    # Documents are purged after the review (LGPD retention)
    assert (
        db_session.exec(
            select(InstructorDocument).where(col(InstructorDocument.instructor_id) == instructor_id)
        ).all()
        == []
    )


def test_admin_instructor_listing_paginates_in_sql(db_session: Session) -> None:
    client = _fresh_client(db_session)
    for i in range(3):
        _register(client, f"page{i}@x.com", ["INSTRUTOR"])
    admin = create_access_token("admin-x", settings=get_settings(), roles=["ADMIN"])

    resp = client.get(
        "/api/v1/admin/instructors?status=PENDENTE&page=2&page_size=2",
        headers={"Authorization": f"Bearer {admin}"},
    )

    assert resp.status_code == 200
    assert resp.json()["meta"]["pagination"] == {"page": 2, "page_size": 2, "total": 3}
    assert len(resp.json()["data"]) == 1
