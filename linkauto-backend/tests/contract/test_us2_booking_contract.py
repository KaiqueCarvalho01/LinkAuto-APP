from datetime import datetime, timedelta, timezone

from app.services.us1_store import get_identity_store
from app.core.security import hash_password


def _setup_instructor_with_slots(token, client):
    now = datetime.now(timezone.utc) + timedelta(hours=4)
    slots = []
    for i in range(3):
        resp = client.post(
            "/api/v1/instructors/me/slots",
            json={
                "starts_at": (now + timedelta(hours=i)).isoformat(),
                "ends_at": (now + timedelta(hours=i + 1)).isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        slots.append(resp.json()["data"]["id"])
    return slots


def _register_login(role, email, client):
    store = get_identity_store()
    user = store.create_user(email, hash_password("Pass1234!"), [role])
    if role == "INSTRUTOR":
        store.update_profile(user.id, {
            "instructor_profile": {
                "full_name": "Test Instructor",
                "phone": "11999999999",
                "city": "Mogi Mirim",
                "state": "SP",
            }
        })
        store.review_instructor(user.id, status="APROVADO", reviewed_by="admin-id")
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "Pass1234!"})
    token = resp.json()["data"]["access_token"]
    return user.id, token


class TestBookingContract:
    def test_create_booking_returns_201(self, client):
        get_identity_store().reset()
        inst_id, inst_token = _register_login("INSTRUTOR", "bookinst@test.com", client)
        stu_id, stu_token = _register_login("ALUNO", "bookstu@test.com", client)
        slot_ids = _setup_instructor_with_slots(inst_token, client)

        resp = client.post(
            "/api/v1/bookings",
            json={
                "instructor_id": inst_id,
                "slot_ids": slot_ids[:2],
            },
            headers={"Authorization": f"Bearer {stu_token}"},
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["status"] == "PENDENTE"

    def test_list_bookings_returns_200(self, client):
        get_identity_store().reset()
        stu_id, stu_token = _register_login("ALUNO", "liststu@test.com", client)
        resp = client.get(
            "/api/v1/bookings",
            headers={"Authorization": f"Bearer {stu_token}"},
        )
        assert resp.status_code == 200
        assert "data" in resp.json()

    def test_create_booking_unauthenticated_returns_401(self, client):
        resp = client.post("/api/v1/bookings", json={"instructor_id": "x", "slot_ids": ["a", "b"]})
        assert resp.status_code == 401
