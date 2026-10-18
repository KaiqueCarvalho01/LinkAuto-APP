"""New accounts need a valid e-mail; existing ones keep working (#81)."""

from typing import TYPE_CHECKING

import pytest

from app.core.security import hash_password
from app.services.identity_repository import IdentityRepository

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session


def _register(client: TestClient, email: str) -> int:
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Pass1234!", "roles": ["ALUNO"]},
    ).status_code


@pytest.mark.parametrize(
    "email",
    ["not-an-email", "ana@", "@test.com", "ana@test", "ana@linkauto.test", f"{'a' * 250}@x.com"],
)
def test_registration_rejects_invalid_emails(client: TestClient, email: str) -> None:
    assert _register(client, email) == 422


def test_registration_accepts_and_normalizes_valid_emails(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "Ana.Souza@Example.COM", "password": "Pass1234!", "roles": ["ALUNO"]},
    )

    assert resp.status_code == 201
    assert resp.json()["data"]["email"] == "ana.souza@example.com"


def test_existing_accounts_with_unusual_emails_can_still_log_in(
    client: TestClient, db_session: Session
) -> None:
    # Created before e-mails were validated (or by the seed): never locked out
    IdentityRepository(db_session).create_user(
        "legacy@seed.test", hash_password("Pass1234!"), ["ALUNO"]
    )
    db_session.commit()

    resp = client.post(
        "/api/v1/auth/login", json={"email": "legacy@seed.test", "password": "Pass1234!"}
    )

    assert resp.status_code == 200
