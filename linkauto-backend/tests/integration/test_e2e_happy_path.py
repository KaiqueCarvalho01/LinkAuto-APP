from datetime import datetime, timedelta, timezone

from app.domain.booking import BookingStatus
from app.models.user import UserRole
from app.core.security import create_access_token
from app.core.config import get_settings


def test_happy_path_e2e_journey(client, db_session):
    """End-to-end happy-path integration smoke test for student-instructor-admin lifecycle."""
    settings = get_settings()

    # 1. Seed users & profiles
    # Student
    resp_student_reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": "student_e2e@test.com",
            "password": "password123",
            "roles": [UserRole.ALUNO.value],
            "fullName": "Student E2E",
            "phone": "11999999999",
            "city": "São Paulo",
            "state": "SP",
        }
    )
    assert resp_student_reg.status_code == 201
    assert resp_student_reg.headers.get("X-Correlation-ID") is not None

    # Instructor
    resp_inst_reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": "inst_e2e@test.com",
            "password": "password123",
            "roles": [UserRole.INSTRUTOR.value],
            "fullName": "Instructor E2E",
            "phone": "11988888888",
            "city": "São Paulo",
            "state": "SP",
        }
    )
    assert resp_inst_reg.status_code == 201
    instructor_id = resp_inst_reg.json()["data"]["id"]

    # 2. Authenticate all roles to obtain JWTs
    # Admin Token (Simulated via token generator)
    admin_token = create_access_token("admin-1", settings=settings, roles=[UserRole.ADMIN.value])
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    # Login Student
    resp_std_login = client.post(
        "/api/v1/auth/login",
        json={"email": "student_e2e@test.com", "password": "password123"}
    )
    assert resp_std_login.status_code == 200
    student_token = resp_std_login.json()["data"]["access_token"]
    headers_student = {"Authorization": f"Bearer {student_token}"}

    # Login Instructor
    resp_inst_login = client.post(
        "/api/v1/auth/login",
        json={"email": "inst_e2e@test.com", "password": "password123"}
    )
    assert resp_inst_login.status_code == 200
    instructor_token = resp_inst_login.json()["data"]["access_token"]
    headers_instructor = {"Authorization": f"Bearer {instructor_token}"}

    # 3. Admin approves the instructor to make them visible
    resp_approve = client.patch(
        f"/api/v1/admin/instructors/{instructor_id}/approve",
        headers=headers_admin
    )
    assert resp_approve.status_code == 200

    # 4. Instructor creates 2 consecutive slots
    now = datetime.now(timezone.utc) + timedelta(hours=2)
    slot1_start = now.replace(minute=0, second=0, microsecond=0)
    slot1_end = slot1_start + timedelta(hours=1)
    slot2_start = slot1_end
    slot2_end = slot2_start + timedelta(hours=1)

    resp_slot1 = client.post(
        "/api/v1/instructors/me/slots",
        json={"starts_at": slot1_start.isoformat(), "ends_at": slot1_end.isoformat()},
        headers=headers_instructor
    )
    assert resp_slot1.status_code == 201
    slot1_id = resp_slot1.json()["data"]["id"]

    resp_slot2 = client.post(
        "/api/v1/instructors/me/slots",
        json={"starts_at": slot2_start.isoformat(), "ends_at": slot2_end.isoformat()},
        headers=headers_instructor
    )
    assert resp_slot2.status_code == 201
    slot2_id = resp_slot2.json()["data"]["id"]

    # 5. Student searches for instructors and verifies visibility
    resp_search = client.get(
        "/api/v1/users/public-instructors?city=S%C3%A3o%20Paulo",
        headers=headers_student
    )
    assert resp_search.status_code == 200
    instructors_list = resp_search.json()["data"]
    assert any(inst["id"] == instructor_id for inst in instructors_list)

    # 6. Student creates a Booking with both slots
    resp_booking = client.post(
        "/api/v1/bookings",
        json={"instructor_id": instructor_id, "slot_ids": [slot1_id, slot2_id]},
        headers=headers_student
    )
    assert resp_booking.status_code == 201
    booking_id = resp_booking.json()["data"]["id"]
    assert resp_booking.json()["data"]["status"] == BookingStatus.PENDENTE.value

    # 7. Instructor confirms the Booking
    resp_confirm = client.patch(
        f"/api/v1/bookings/{booking_id}/confirm",
        headers=headers_instructor
    )
    assert resp_confirm.status_code == 200
    assert resp_confirm.json()["data"]["status"] == BookingStatus.CONFIRMADA.value

    # 8. Admin triggers the completion job to complete the lesson (simulating time passing)
    # Manually backdate slot times to be in the past to trigger completion
    from app.models.slot import Slot
    db_session.query(Slot).filter(Slot.id.in_([slot1_id, slot2_id])).update({
        "starts_at": datetime.now(timezone.utc) - timedelta(hours=5),
        "ends_at": datetime.now(timezone.utc) - timedelta(hours=3),
    })
    db_session.commit()

    resp_job = client.post(
        "/api/v1/jobs/booking-completion",
        headers=headers_admin
    )
    assert resp_job.status_code == 200
    assert resp_job.json()["data"]["processed"] == 1
    assert booking_id in resp_job.json()["data"]["errors"]

    # Verify status is now REALIZADA
    resp_get_booking = client.get(f"/api/v1/bookings/{booking_id}/messages", headers=headers_student)
    assert resp_get_booking.status_code == 200

    # 9. Student and Instructor exchange messages
    resp_msg1 = client.post(
        f"/api/v1/bookings/{booking_id}/messages",
        json={"content": "Olá, instrutor! A aula foi excelente!"},
        headers=headers_student
    )
    assert resp_msg1.status_code == 201

    resp_msg2 = client.post(
        f"/api/v1/bookings/{booking_id}/messages",
        json={"content": "Obrigado! Você se saiu muito bem!"},
        headers=headers_instructor
    )
    assert resp_msg2.status_code == 201

    # 10. Student reviews Instructor (Rating = 5)
    resp_rev_std = client.post(
        f"/api/v1/bookings/{booking_id}/reviews",
        json={"rating": 5, "comment": "Instrutor muito atencioso."},
        headers=headers_student
    )
    assert resp_rev_std.status_code == 201

    # 11. Instructor reviews Student (Rating = 4)
    resp_rev_inst = client.post(
        f"/api/v1/bookings/{booking_id}/reviews",
        json={"rating": 4, "comment": "Aluno dedicado."},
        headers=headers_instructor
    )
    assert resp_rev_inst.status_code == 201

    # 12. Check public reviews and instructor's average rating update
    resp_reviews = client.get(f"/api/v1/instructors/{instructor_id}/reviews")
    assert resp_reviews.status_code == 200
    reviews_list = resp_reviews.json()["data"]
    assert len(reviews_list) == 1
    assert reviews_list[0]["rating"] == 5
    assert reviews_list[0]["comment"] == "Instrutor muito atencioso."
