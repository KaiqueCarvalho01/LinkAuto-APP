"""Deactivated accounts (users.is_active = false) cannot log in, refresh or call the API (#22)."""

from typing import TYPE_CHECKING, Any

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
from app.services.identity_repository import IdentityRepository

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session

    from app.models import User

PASSWORD = "password123"


def _create_user(db_session: Session, email: str, roles: list[str] | None = None) -> User:
    user = IdentityRepository(db_session).create_user(
        email, hash_password(PASSWORD), roles or ["ALUNO"]
    )
    db_session.commit()
    return user


def _deactivate(db_session: Session, user: User) -> None:
    user.is_active = False
    db_session.commit()


def _login(client: TestClient, email: str, password: str = PASSWORD) -> tuple[int, dict[str, Any]]:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.status_code, resp.json()


def test_inactive_user_cannot_log_in_and_gets_the_generic_error(
    client: TestClient, db_session: Session
) -> None:
    user = _create_user(db_session, "banned@x.com")
    _deactivate(db_session, user)

    status, body = _login(client, "banned@x.com")
    wrong_status, wrong_body = _login(client, "banned@x.com", "wrong-password")
    unknown_status, unknown_body = _login(client, "nobody@x.com")

    assert status == wrong_status == unknown_status == 401
    # Same message as wrong credentials: the response doesn't reveal that the account exists
    assert body["error"] == wrong_body["error"] == unknown_body["error"]


def test_inactive_user_cannot_refresh(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "refresh-ban@x.com")
    resp = client.post(
        "/api/v1/auth/login", json={"email": "refresh-ban@x.com", "password": PASSWORD}
    )
    assert resp.status_code == 200
    refresh_cookie = resp.cookies.get("refresh_token")
    assert refresh_cookie

    _deactivate(db_session, user)
    client.cookies.set("refresh_token", refresh_cookie)
    resp = client.post("/api/v1/auth/refresh")

    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_inactive_user_access_token_is_rejected(client: TestClient, db_session: Session) -> None:
    user = _create_user(db_session, "token-ban@x.com")
    token = create_access_token(user.id, settings=get_settings(), roles=user.roles)
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/v1/users/me", headers=headers).status_code == 200

    _deactivate(db_session, user)

    resp = client.get("/api/v1/users/me", headers=headers)
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_access_token_of_deleted_user_is_rejected(client: TestClient) -> None:
    token = create_access_token("ghost-user", settings=get_settings(), roles=["ADMIN"])

    resp = client.get("/api/v1/admin/instructors", headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 401


def test_roles_come_from_the_database_not_the_token(
    client: TestClient, db_session: Session
) -> None:
    """A token minted while the user was ADMIN stops granting ADMIN once the role is removed."""
    user = _create_user(db_session, "demoted@x.com", ["ALUNO"])
    token = create_access_token(user.id, settings=get_settings(), roles=["ADMIN"])

    resp = client.get("/api/v1/admin/instructors", headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 403
