from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.core.security import hash_password
from app.services.identity_repository import IdentityRepository

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session


def _register_and_login_instructor(client: TestClient, db_session: Session) -> str:
    store = IdentityRepository(db_session)
    user = store.create_user("inst@test.com", hash_password("Pass1234!"), ["INSTRUTOR"])
    store.update_profile(
        user.id,
        {
            "instructor_profile": {
                "full_name": "Test Instructor",
                "phone": "11999999999",
                "city": "Mogi Mirim",
                "state": "SP",
            }
        },
    )
    store.review_instructor(user.id, status="APROVADO", reviewed_by="admin-id")
    resp = client.post(
        "/api/v1/auth/login", json={"email": "inst@test.com", "password": "Pass1234!"}
    )
    return resp.json()["data"]["access_token"]


class TestSlotEndpoints:
    def test_create_slot_returns_201(self, client: TestClient, db_session: Session) -> None:
        token = _register_and_login_instructor(client, db_session)
        now = datetime.now(UTC) + timedelta(hours=2)
        resp = client.post(
            "/api/v1/instructors/me/slots",
            json={
                "starts_at": now.isoformat(),
                "ends_at": (now + timedelta(hours=1)).isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["status"] == "DISPONIVEL"

    def test_list_slots_returns_200(self, client: TestClient, db_session: Session) -> None:
        token = _register_and_login_instructor(client, db_session)
        resp = client.get(
            "/api/v1/instructors/me/slots",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert "data" in resp.json()

    def test_create_slot_rejects_unauthenticated(self, client: TestClient) -> None:
        now = datetime.now(UTC) + timedelta(hours=2)
        resp = client.post(
            "/api/v1/instructors/me/slots",
            json={
                "starts_at": now.isoformat(),
                "ends_at": (now + timedelta(hours=1)).isoformat(),
            },
        )
        assert resp.status_code == 401
