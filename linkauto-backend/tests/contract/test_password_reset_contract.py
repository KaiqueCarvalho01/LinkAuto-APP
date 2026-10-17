"""Password reset: request, confirm, and the admin-issued link used without e-mail (#52)."""

from datetime import timedelta
from typing import TYPE_CHECKING, cast
from urllib.parse import parse_qs, urlparse

import pytest
from sqlmodel import col, select

from app.models import PasswordResetToken, RefreshToken
from app.models.base import utc_now
from app.services.dependencies import get_notification_service
from app.services.notification_service import DisabledEmailGateway, NotificationService
from tests.factories import admin_headers, auth_headers, seed_student

if TYPE_CHECKING:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from sqlmodel import Session

    from app.services.notification_service import InMemoryEmailGateway

EMAIL = "reset-me@test.com"
OLD_PASSWORD = "OldPass123!"
NEW_PASSWORD = "NewPass456!"


def _register(client: TestClient) -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": EMAIL, "password": OLD_PASSWORD, "roles": ["ALUNO"]},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


def _login_status(client: TestClient, password: str) -> int:
    return client.post(
        "/api/v1/auth/login", json={"email": EMAIL, "password": password}
    ).status_code


def _token_from(url: str) -> str:
    parsed = urlparse(url)
    assert parsed.path == "/password-reset/confirm"
    return parse_qs(parsed.query)["token"][0]


def _emailed_token(outbox: InMemoryEmailGateway) -> str:
    message = outbox.sent_messages[-1]
    assert message["recipients"] == [EMAIL]
    url = next(word for word in str(message["body"]).split() if "/password-reset/confirm" in word)
    return _token_from(url)


def _confirm(client: TestClient, token: str, password: str = NEW_PASSWORD) -> int:
    return client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": token, "new_password": password},
    ).status_code


def test_emailed_link_sets_a_new_password_once(
    client: TestClient, db_session: Session, email_outbox: InMemoryEmailGateway
) -> None:
    user_id = _register(client)
    assert _login_status(client, OLD_PASSWORD) == 200

    resp = client.post("/api/v1/auth/password-reset", json={"email": EMAIL})
    assert resp.status_code == 202
    token = _emailed_token(email_outbox)

    assert _confirm(client, token) == 200
    assert _login_status(client, NEW_PASSWORD) == 200
    assert _login_status(client, OLD_PASSWORD) == 401
    # Single use
    assert _confirm(client, token, "Another789!") == 400
    # Only the hash is stored
    stored = db_session.exec(select(PasswordResetToken)).all()
    assert all(token not in row.token_hash for row in stored)
    # Sessions from before the reset are signed out (the new login's token is the only live one)
    live = db_session.exec(
        select(RefreshToken).where(
            col(RefreshToken.user_id) == user_id, col(RefreshToken.revoked_at).is_(None)
        )
    ).all()
    assert len(live) == 1


def test_unknown_email_is_accepted_without_sending(
    client: TestClient, db_session: Session, email_outbox: InMemoryEmailGateway
) -> None:
    resp = client.post("/api/v1/auth/password-reset", json={"email": "nobody@test.com"})

    assert resp.status_code == 202
    assert email_outbox.sent_messages == []
    assert db_session.exec(select(PasswordResetToken)).all() == []


def test_a_new_link_replaces_the_previous_one(
    client: TestClient, email_outbox: InMemoryEmailGateway
) -> None:
    _register(client)
    client.post("/api/v1/auth/password-reset", json={"email": EMAIL})
    first = _emailed_token(email_outbox)
    client.post("/api/v1/auth/password-reset", json={"email": EMAIL})
    second = _emailed_token(email_outbox)

    assert _confirm(client, first) == 400
    assert _confirm(client, second) == 200


def test_expired_link_is_rejected(
    client: TestClient, db_session: Session, email_outbox: InMemoryEmailGateway
) -> None:
    _register(client)
    client.post("/api/v1/auth/password-reset", json={"email": EMAIL})
    token = _emailed_token(email_outbox)
    stored = db_session.exec(select(PasswordResetToken)).one()
    stored.expires_at = utc_now() - timedelta(minutes=1)
    db_session.commit()

    resp = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": token, "new_password": NEW_PASSWORD},
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_TOKEN"


@pytest.mark.parametrize(
    ("token", "password", "expected"), [("bogus", NEW_PASSWORD, 400), ("x", "short", 422)]
)
def test_confirm_rejects_bad_input(
    client: TestClient, token: str, password: str, expected: int
) -> None:
    assert _confirm(client, token, password) == expected


class TestWithoutEmail:
    @pytest.fixture(autouse=True)
    def _disable_email(self, client: TestClient) -> None:
        app = cast("FastAPI", client.app)
        app.dependency_overrides[get_notification_service] = lambda: NotificationService(
            DisabledEmailGateway()
        )

    def test_request_still_answers_202(self, client: TestClient) -> None:
        _register(client)

        resp = client.post("/api/v1/auth/password-reset", json={"email": EMAIL})

        assert resp.status_code == 202

    def test_admin_issued_link_resets_the_password(
        self, client: TestClient, db_session: Session
    ) -> None:
        user_id = _register(client)

        resp = client.post(
            f"/api/v1/admin/users/{user_id}/password-reset-link",
            headers=admin_headers(db_session),
        )

        assert resp.status_code == 201
        data = resp.json()["data"]
        assert set(data) == {"reset_url", "expires_at"}
        assert _confirm(client, _token_from(data["reset_url"])) == 200
        assert _login_status(client, NEW_PASSWORD) == 200

    def test_only_admins_can_issue_links(self, client: TestClient, db_session: Session) -> None:
        user_id = _register(client)
        student = seed_student(db_session, "stu-reset").user

        resp = client.post(
            f"/api/v1/admin/users/{user_id}/password-reset-link", headers=auth_headers(student)
        )

        assert resp.status_code == 403

    def test_unknown_user_returns_404(self, client: TestClient, db_session: Session) -> None:
        resp = client.post(
            "/api/v1/admin/users/missing/password-reset-link",
            headers=admin_headers(db_session),
        )

        assert resp.status_code == 404
