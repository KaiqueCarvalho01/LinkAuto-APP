
from app.models.booking import Booking
from app.models.user import User, StudentProfile, InstructorProfile, UserRole, DetranStatus
from app.core.security import create_access_token
from app.core.config import get_settings


def _seed_auth_users(db_session):
    settings = get_settings()
    student = User(id="student-1", email="student@test.com", password_hash="h", roles=[UserRole.ALUNO.value])
    stu_profile = StudentProfile(user_id="student-1", full_name="Student", phone="1", city="C", state="SP")
    
    instructor = User(id="instructor-1", email="instructor@test.com", password_hash="h", roles=[UserRole.INSTRUTOR.value])
    inst_profile = InstructorProfile(user_id="instructor-1", full_name="Instructor", phone="2", city="C", state="SP", detran_status=DetranStatus.APROVADO)
    
    intruder = User(id="intruder-1", email="intruder@test.com", password_hash="h", roles=[UserRole.ALUNO.value])
    int_profile = StudentProfile(user_id="intruder-1", full_name="Intruder", phone="3", city="C", state="SP")

    db_session.add_all([student, stu_profile, instructor, inst_profile, intruder, int_profile])
    db_session.flush()

    student_token = create_access_token("student-1", settings=settings, roles=[UserRole.ALUNO.value])
    instructor_token = create_access_token("instructor-1", settings=settings, roles=[UserRole.INSTRUTOR.value])
    intruder_token = create_access_token("intruder-1", settings=settings, roles=[UserRole.ALUNO.value])

    return student_token, instructor_token, intruder_token


def test_booking_messages_endpoints_contract_and_auth(client, db_session):
    """POST and GET /bookings/{id}/messages validate participants and return correctly formatted envelope."""
    student_token, instructor_token, intruder_token = _seed_auth_users(db_session)
    
    # Create booking
    booking = Booking(
        id="booking-123",
        student_id="student-1",
        instructor_id="instructor-1",
        status="CONFIRMADA",
    )
    db_session.add(booking)
    db_session.flush()

    headers_student = {"Authorization": f"Bearer {student_token}"}
    headers_intruder = {"Authorization": f"Bearer {intruder_token}"}

    # 1. Post message by unauthorized user -> 403 Forbidden/Access Error
    response = client.post(
        "/api/v1/bookings/booking-123/messages",
        json={"content": "Olá!"},
        headers=headers_intruder,
    )
    assert response.status_code in (403, 404)

    # 2. Post message by student -> 201 Created and envelope formatting
    response = client.post(
        "/api/v1/bookings/booking-123/messages",
        json={"content": "Olá, instrutor!"},
        headers=headers_student,
    )
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["error"] is None
    assert json_data["data"]["content"] == "Olá, instrutor!"
    assert json_data["data"]["booking_id"] == "booking-123"
    assert json_data["data"]["sender_id"] == "student-1"
    assert json_data["data"]["created_at"].endswith("Z")

    # 3. Get messages list -> 200 OK and chronological envelope formatting
    response = client.get(
        "/api/v1/bookings/booking-123/messages?page=1&page_size=10",
        headers=headers_student,
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["error"] is None
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["content"] == "Olá, instrutor!"
    assert json_data["data"][0]["created_at"].endswith("Z")


def test_booking_reviews_endpoints_contract_and_auth(client, db_session):
    """POST /bookings/{id}/reviews and GET /instructors/{id}/reviews enforce business rules and validate contract."""
    student_token, instructor_token, intruder_token = _seed_auth_users(db_session)
    
    # Create non-realizada booking
    booking_pending = Booking(
        id="booking-pending",
        student_id="student-1",
        instructor_id="instructor-1",
        status="CONFIRMADA",
    )
    # Create realizada booking
    booking_done = Booking(
        id="booking-done",
        student_id="student-1",
        instructor_id="instructor-1",
        status="REALIZADA",
    )
    db_session.add_all([booking_pending, booking_done])
    db_session.flush()

    headers_student = {"Authorization": f"Bearer {student_token}"}
    headers_intruder = {"Authorization": f"Bearer {intruder_token}"}

    # 1. Post review for non-realizada booking -> 409 Conflict
    response = client.post(
        "/api/v1/bookings/booking-pending/reviews",
        json={"rating": 5, "comment": "Tarde demais"},
        headers=headers_student,
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"

    # 2. Post review by unauthorized intruder -> 403 Forbidden
    response = client.post(
        "/api/v1/bookings/booking-done/reviews",
        json={"rating": 5, "comment": "Hacker"},
        headers=headers_intruder,
    )
    assert response.status_code in (403, 404)

    # 3. Post review by student -> 201 Created and envelope formatting
    response = client.post(
        "/api/v1/bookings/booking-done/reviews",
        json={"rating": 5, "comment": "Melhor aula!"},
        headers=headers_student,
    )
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["error"] is None
    assert json_data["data"]["rating"] == 5
    assert json_data["data"]["comment"] == "Melhor aula!"
    assert json_data["data"]["created_at"].endswith("Z")

    # 4. Post duplicate review -> 409 Conflict
    response = client.post(
        "/api/v1/bookings/booking-done/reviews",
        json={"rating": 4, "comment": "Mais uma"},
        headers=headers_student,
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"

    # 5. List instructor reviews -> 200 OK and reviews listing envelope
    response = client.get("/api/v1/instructors/instructor-1/reviews?page=1&page_size=10")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["error"] is None
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["rating"] == 5
    assert json_data["data"][0]["comment"] == "Melhor aula!"
    assert json_data["data"][0]["created_at"].endswith("Z")
