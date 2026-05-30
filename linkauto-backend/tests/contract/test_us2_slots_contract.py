from datetime import datetime, timedelta, timezone

from app.services.us1_store import get_identity_store
from app.core.security import hash_password


def _register_and_login_instructor(client):
    store = get_identity_store()
    store.reset()
    user = store.create_user("inst@test.com", hash_password("Pass1234!"), ["INSTRUTOR"])
    store.update_profile(user.id, {
        "instructor_profile": {
            "full_name": "Test Instructor",
            "phone": "11999999999",
            "city": "Mogi Mirim",
            "state": "SP",
        }
    })
    store.review_instructor(user.id, status="APROVADO", reviewed_by="admin-id")
    resp = client.post("/api/v1/auth/login", json={"email": "inst@test.com", "password": "Pass1234!"})
    return resp.json()["data"]["access_token"]


class TestSlotEndpoints:
    def test_create_slot_returns_201(self, client):
        token = _register_and_login_instructor(client)
        now = datetime.now(timezone.utc) + timedelta(hours=2)
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

    def test_list_slots_returns_200(self, client):
        token = _register_and_login_instructor(client)
        resp = client.get(
            "/api/v1/instructors/me/slots",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert "data" in resp.json()

    def test_create_slot_rejects_unauthenticated(self, client):
        now = datetime.now(timezone.utc) + timedelta(hours=2)
        resp = client.post(
            "/api/v1/instructors/me/slots",
            json={
                "starts_at": now.isoformat(),
                "ends_at": (now + timedelta(hours=1)).isoformat(),
            },
        )
        assert resp.status_code == 401
