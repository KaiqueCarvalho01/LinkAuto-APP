from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.core.security import hash_password
from app.services.us1_store import get_identity_store

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def _setup_instructor_with_slots(token: str, client: TestClient) -> list[str]:
    now = datetime.now(UTC) + timedelta(hours=4)
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


def _register_login(role: str, email: str, client: TestClient) -> tuple[str, str]:
    store = get_identity_store()
    user = store.create_user(email, hash_password("Pass1234!"), [role])
    if role == "INSTRUTOR":
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
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "Pass1234!"})
    token = resp.json()["data"]["access_token"]
    return user.id, token


class TestBookingContract:
    def test_create_booking_returns_201(self, client: TestClient) -> None:
        get_identity_store().reset()
        inst_id, inst_token = _register_login("INSTRUTOR", "bookinst@test.com", client)
        _, stu_token = _register_login("ALUNO", "bookstu@test.com", client)
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

    def test_create_booking_persists_meeting_location(self, client: TestClient) -> None:
        get_identity_store().reset()
        inst_id, inst_token = _register_login("INSTRUTOR", "locinst@test.com", client)
        _, stu_token = _register_login("ALUNO", "locstu@test.com", client)
        slot_ids = _setup_instructor_with_slots(inst_token, client)

        resp = client.post(
            "/api/v1/bookings",
            json={
                "instructor_id": inst_id,
                "slot_ids": slot_ids[:2],
                "location_description": "Praça central",
                "latitude": -22.43,
                "longitude": -46.95,
            },
            headers={"Authorization": f"Bearer {stu_token}"},
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["location_description"] == "Praça central"
        assert data["latitude"] == -22.43
        assert data["longitude"] == -46.95

    def test_list_bookings_returns_200(self, client: TestClient) -> None:
        get_identity_store().reset()
        _, stu_token = _register_login("ALUNO", "liststu@test.com", client)
        resp = client.get(
            "/api/v1/bookings",
            headers={"Authorization": f"Bearer {stu_token}"},
        )
        assert resp.status_code == 200
        assert "data" in resp.json()

    def test_create_booking_unauthenticated_returns_401(self, client: TestClient) -> None:
        resp = client.post("/api/v1/bookings", json={"instructor_id": "x", "slot_ids": ["a", "b"]})
        assert resp.status_code == 401

    def test_confirm_missing_booking_returns_404(self, client: TestClient) -> None:
        _, inst_token = _register_login("INSTRUTOR", "confirm404@test.com", client)

        resp = client.patch(
            "/api/v1/bookings/does-not-exist/confirm",
            headers={"Authorization": f"Bearer {inst_token}"},
        )
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "NOT_FOUND"

    def test_confirm_booking_by_other_instructor_returns_403(self, client: TestClient) -> None:
        inst_id, inst_token = _register_login("INSTRUTOR", "confirmowner@test.com", client)
        _, other_token = _register_login("INSTRUTOR", "confirmother@test.com", client)
        _, stu_token = _register_login("ALUNO", "confirmstu@test.com", client)
        slot_ids = _setup_instructor_with_slots(inst_token, client)
        booking_id = client.post(
            "/api/v1/bookings",
            json={"instructor_id": inst_id, "slot_ids": slot_ids[:2]},
            headers={"Authorization": f"Bearer {stu_token}"},
        ).json()["data"]["id"]

        resp = client.patch(
            f"/api/v1/bookings/{booking_id}/confirm",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "FORBIDDEN"

    def test_cancel_booking_by_non_participant_returns_403(self, client: TestClient) -> None:
        get_identity_store().reset()
        inst_id, inst_token = _register_login("INSTRUTOR", "cancelinst@test.com", client)
        _, stu_token = _register_login("ALUNO", "cancelstu@test.com", client)
        _, intruder_token = _register_login("ALUNO", "cancelintruder@test.com", client)
        slot_ids = _setup_instructor_with_slots(inst_token, client)
        booking_id = client.post(
            "/api/v1/bookings",
            json={"instructor_id": inst_id, "slot_ids": slot_ids[:2]},
            headers={"Authorization": f"Bearer {stu_token}"},
        ).json()["data"]["id"]

        resp = client.patch(
            f"/api/v1/bookings/{booking_id}/cancel",
            json={"reason": "not mine"},
            headers={"Authorization": f"Bearer {intruder_token}"},
        )
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "FORBIDDEN"

        resp = client.get(
            f"/api/v1/bookings/{booking_id}",
            headers={"Authorization": f"Bearer {stu_token}"},
        )
        assert resp.json()["data"]["status"] == "PENDENTE"
