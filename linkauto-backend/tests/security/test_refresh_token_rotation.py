"""Refresh tokens are single-use, reuse revokes the family, and logout revokes (#21)."""

from typing import TYPE_CHECKING

from sqlmodel import col, select

from app.core.config import get_settings
from app.core.security import create_refresh_token, decode_token, hash_password
from app.models import RefreshToken
from app.services.identity_repository import IdentityRepository

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session

PASSWORD = "password123"


def _login(client: TestClient, db_session: Session, email: str = "rotate@x.com") -> str:
    if IdentityRepository(db_session).get_user_by_email(email) is None:
        IdentityRepository(db_session).create_user(email, hash_password(PASSWORD), ["ALUNO"])
        db_session.commit()
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 200
    token = resp.cookies.get("refresh_token")
    assert token
    client.cookies.clear()
    return token


def _refresh(client: TestClient, token: str) -> tuple[int, str | None]:
    client.cookies.set("refresh_token", token)
    resp = client.post("/api/v1/auth/refresh")
    new_token = resp.cookies.get("refresh_token")
    client.cookies.clear()
    return resp.status_code, new_token


def test_rotated_refresh_token_cannot_be_used_again(
    client: TestClient, db_session: Session
) -> None:
    token_a = _login(client, db_session)

    status, token_b = _refresh(client, token_a)
    assert status == 200
    assert token_b
    assert token_b != token_a

    status, _ = _refresh(client, token_a)
    assert status == 401


def test_reusing_a_rotated_token_revokes_the_whole_family(
    client: TestClient, db_session: Session
) -> None:
    token_a = _login(client, db_session)
    _, token_b = _refresh(client, token_a)
    assert token_b

    # An attacker replays the stolen, already-rotated token A...
    assert _refresh(client, token_a)[0] == 401
    # ...so the legitimate user's current token B is revoked as well.
    assert _refresh(client, token_b)[0] == 401


def test_other_sessions_survive_reuse_detection(client: TestClient, db_session: Session) -> None:
    phone = _login(client, db_session)
    laptop_a = _login(client, db_session)
    _refresh(client, laptop_a)
    _refresh(client, laptop_a)  # reuse -> revokes only the laptop's family

    assert _refresh(client, phone)[0] == 200


def test_logout_revokes_the_refresh_token_and_clears_the_cookie(
    client: TestClient, db_session: Session
) -> None:
    token = _login(client, db_session)

    client.cookies.set("refresh_token", token)
    resp = client.post("/api/v1/auth/logout")
    client.cookies.clear()

    assert resp.status_code == 204
    set_cookie = resp.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie
    assert "Max-Age=0" in set_cookie
    assert _refresh(client, token)[0] == 401


def test_logout_without_cookie_is_a_no_op(client: TestClient) -> None:
    assert client.post("/api/v1/auth/logout").status_code == 204


def test_refresh_rejects_a_validly_signed_token_that_was_never_issued(
    client: TestClient, db_session: Session
) -> None:
    user = IdentityRepository(db_session).create_user(
        "forged@x.com", hash_password(PASSWORD), ["ALUNO"]
    )
    db_session.commit()
    forged = create_refresh_token(user.id, settings=get_settings(), roles=user.roles)

    assert _refresh(client, forged)[0] == 401


def test_issued_refresh_tokens_are_stored(client: TestClient, db_session: Session) -> None:
    token = _login(client, db_session)
    jti = decode_token(token, get_settings(), expected_type="refresh").jti

    stored = db_session.exec(select(RefreshToken).where(col(RefreshToken.jti) == jti)).one()
    assert stored.used_at is None
    assert stored.revoked_at is None


def test_refresh_cookie_is_scoped_to_the_auth_endpoints(
    client: TestClient, db_session: Session
) -> None:
    IdentityRepository(db_session).create_user("scope@x.com", hash_password(PASSWORD), ["ALUNO"])
    db_session.commit()

    resp = client.post("/api/v1/auth/login", json={"email": "scope@x.com", "password": PASSWORD})

    assert "Path=/api/v1/auth" in resp.headers["set-cookie"]
