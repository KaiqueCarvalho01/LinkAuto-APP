
from app.domain.booking import BookingStatus
from app.models.booking import Booking
from app.models.user import User, StudentProfile, InstructorProfile, UserRole, DetranStatus
from app.services.booking_message_service import BookingMessageService
from app.services.review_service import ReviewService
from app.services.dependencies import get_notification_service


def _setup_integration_data(db_session):
    student = User(id="student-1", email="student@test.com", password_hash="h", roles=[UserRole.ALUNO.value])
    stu_profile = StudentProfile(user_id="student-1", full_name="Student One", phone="1", city="C", state="SP")
    
    instructor = User(id="instructor-1", email="instructor@test.com", password_hash="h", roles=[UserRole.INSTRUTOR.value])
    inst_profile = InstructorProfile(
        user_id="instructor-1",
        full_name="Instructor One",
        phone="2",
        city="C",
        state="SP",
        detran_status=DetranStatus.APROVADO,
        rating_avg=0.0,
        rating_count=0,
    )

    db_session.add_all([student, stu_profile, instructor, inst_profile])
    db_session.flush()


def test_integration_messages_and_reviews_lifecycle(db_session):
    """Full integration test verifying chronological chat messages, email notifications and rating recals."""
    _setup_integration_data(db_session)
    
    # 1. Create booking in CONFIRMADA status
    booking = Booking(
        id="booking-123",
        student_id="student-1",
        instructor_id="instructor-1",
        status="CONFIRMADA",
    )
    db_session.add(booking)
    db_session.flush()

    # Get notification singleton and clear its gateway list
    notification_svc = get_notification_service()
    notification_svc._email_gateway.sent_messages.clear()

    message_svc = BookingMessageService(db_session, notification_service=notification_svc)
    review_svc = ReviewService(db_session, notification_service=notification_svc)

    # 2. Student sends message
    msg = message_svc.send_message(
        booking_id="booking-123",
        sender_id="student-1",
        content="Olá professor, chego em 5 minutos!",
        sender_email="student@test.com",
        recipient_email="instructor@test.com",
    )
    db_session.flush()

    assert msg.id is not None
    
    # Verify new booking message email notification was sent
    sent_emails = notification_svc._email_gateway.sent_messages
    assert len(sent_emails) == 1
    assert sent_emails[0]["recipients"] == ["instructor@test.com"]
    assert "chego em 5 minutos" in sent_emails[0]["body"]

    # 3. Transition booking to REALIZADA to test reviews
    booking.status = BookingStatus.REALIZADA.value
    db_session.flush()

    # Clear sent emails list
    notification_svc._email_gateway.sent_messages.clear()

    # 4. Student reviews Instructor (Rating = 5)
    review_student = review_svc.create_review(
        booking_id="booking-123",
        reviewer_id="student-1",
        rating=5,
        comment="Instrutor fantástico, recomendo!",
        recipient_email="instructor@test.com",
    )
    db_session.flush()

    assert review_student.id is not None
    
    # Verify instructor profile has been recalculated
    inst_profile = db_session.query(InstructorProfile).filter(InstructorProfile.user_id == "instructor-1").first()
    assert inst_profile.rating_count == 1
    assert float(inst_profile.rating_avg) == 5.0

    # Verify review received email notification sent to instructor
    assert len(sent_emails) == 1
    assert sent_emails[0]["recipients"] == ["instructor@test.com"]
    assert "fantástico" in sent_emails[0]["body"]
    assert "5 estrelas" in sent_emails[0]["body"]

    # 5. Instructor reviews Student (Rating = 4)
    # Clear sent emails list
    notification_svc._email_gateway.sent_messages.clear()
    
    review_instructor = review_svc.create_review(
        booking_id="booking-123",
        reviewer_id="instructor-1",
        rating=4,
        comment="Aluno pontual e focado.",
        recipient_email="student@test.com",
    )
    db_session.flush()

    assert review_instructor.id is not None

    # Student rating and count should remain unchanged (since students are not rankable in V1)
    # Verify review received email notification sent to student
    assert len(sent_emails) == 1
    assert sent_emails[0]["recipients"] == ["student@test.com"]
    assert "pontual" in sent_emails[0]["body"]
    assert "4 estrelas" in sent_emails[0]["body"]
