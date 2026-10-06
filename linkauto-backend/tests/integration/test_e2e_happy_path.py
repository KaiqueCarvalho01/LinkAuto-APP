from datetime import UTC, datetime, timedelta

from app.core.config import get_settings
from app.core.security import create_access_token
from app.domain.booking import BookingStatus
from app.models.slot import Slot
from app.models.user import UserRole


def _register(client, email, role, full_name, phone):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "roles": [role.value],
            "fullName": full_name,
            "phone": phone,
            "city": "São Paulo",
            "state": "SP",
        },
    )
    assert resp.status_code == 201
    assert resp.headers.get("X-Correlation-ID") is not None
    return resp.json()["data"]["id"]


def _login(client, email):
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['data']['access_token']}"}


def _create_consecutive_slots(client, headers_instructor):
    start = (datetime.now(UTC) + timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)
    slot_ids = []
    for i in range(2):
        resp = client.post(
            "/api/v1/instructors/me/slots",
            json={
                "starts_at": (start + timedelta(hours=i)).isoformat(),
                "ends_at": (start + timedelta(hours=i + 1)).isoformat(),
            },
            headers=headers_instructor,
        )
        assert resp.status_code == 201
        slot_ids.append(resp.json()["data"]["id"])
    return slot_ids


def _complete_booking(client, db_session, booking_id, slot_ids, headers_admin):
    """Backdate the slots (simulating time passing) and run the completion job."""
    db_session.query(Slot).filter(Slot.id.in_(slot_ids)).update(
        {
            "starts_at": datetime.now(UTC) - timedelta(hours=5),
            "ends_at": datetime.now(UTC) - timedelta(hours=3),
        }
    )
    db_session.commit()

    resp_job = client.post("/api/v1/jobs/booking-completion", headers=headers_admin)
    assert resp_job.status_code == 200
    assert resp_job.json()["data"]["processed"] == 1
    assert booking_id in resp_job.json()["data"]["errors"]


def _post(client, url, payload, headers):
    resp = client.post(url, json=payload, headers=headers)
    assert resp.status_code == 201
    return resp


def test_happy_path_e2e_journey(client, db_session):
    """End-to-end happy-path integration smoke test for student-instructor-admin lifecycle."""
    # 1. Register users and authenticate all roles
    _register(client, "student_e2e@test.com", UserRole.ALUNO, "Student E2E", "11999999999")
    instructor_id = _register(
        client, "inst_e2e@test.com", UserRole.INSTRUTOR, "Instructor E2E", "11988888888"
    )
    admin_token = create_access_token(
        "admin-1", settings=get_settings(), roles=[UserRole.ADMIN.value]
    )
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_student = _login(client, "student_e2e@test.com")
    headers_instructor = _login(client, "inst_e2e@test.com")

    # 2. Admin approves the instructor to make them visible
    resp = client.patch(f"/api/v1/admin/instructors/{instructor_id}/approve", headers=headers_admin)
    assert resp.status_code == 200

    # 3. Instructor creates 2 consecutive slots
    slot_ids = _create_consecutive_slots(client, headers_instructor)

    # 4. Student searches for instructors and verifies visibility
    resp = client.get(
        "/api/v1/users/public-instructors?city=S%C3%A3o%20Paulo", headers=headers_student
    )
    assert resp.status_code == 200
    assert any(inst["id"] == instructor_id for inst in resp.json()["data"])

    # 5. Student books both slots; instructor confirms
    resp = _post(
        client,
        "/api/v1/bookings",
        {"instructor_id": instructor_id, "slot_ids": slot_ids},
        headers_student,
    )
    booking_id = resp.json()["data"]["id"]
    assert resp.json()["data"]["status"] == BookingStatus.PENDENTE.value

    resp = client.patch(f"/api/v1/bookings/{booking_id}/confirm", headers=headers_instructor)
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == BookingStatus.CONFIRMADA.value

    # 6. The lesson takes place and the completion job marks it REALIZADA
    _complete_booking(client, db_session, booking_id, slot_ids, headers_admin)
    resp = client.get(f"/api/v1/bookings/{booking_id}/messages", headers=headers_student)
    assert resp.status_code == 200

    # 7. Student and instructor exchange messages, then review each other
    messages_url = f"/api/v1/bookings/{booking_id}/messages"
    _post(
        client, messages_url, {"content": "Olá, instrutor! A aula foi excelente!"}, headers_student
    )
    _post(
        client, messages_url, {"content": "Obrigado! Você se saiu muito bem!"}, headers_instructor
    )

    reviews_url = f"/api/v1/bookings/{booking_id}/reviews"
    _post(
        client, reviews_url, {"rating": 5, "comment": "Instrutor muito atencioso."}, headers_student
    )
    _post(client, reviews_url, {"rating": 4, "comment": "Aluno dedicado."}, headers_instructor)

    # 8. Only the student's review of the instructor is public
    resp = client.get(f"/api/v1/instructors/{instructor_id}/reviews")
    assert resp.status_code == 200
    reviews_list = resp.json()["data"]
    assert len(reviews_list) == 1
    assert reviews_list[0]["rating"] == 5
    assert reviews_list[0]["comment"] == "Instrutor muito atencioso."
