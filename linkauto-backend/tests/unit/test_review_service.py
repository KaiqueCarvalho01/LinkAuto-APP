import pytest

from app.models.booking import Booking
from app.models.user import User, InstructorProfile, StudentProfile
from app.models.review import Review
from app.services.review_service import ReviewService, ReviewAccessError, ReviewStateError, ReviewDuplicateError
from app.services.notification_service import NotificationService, InMemoryEmailGateway


@pytest.fixture
def mock_notification_service():
    gateway = InMemoryEmailGateway()
    return NotificationService(email_gateway=gateway), gateway


def test_create_review_valid_student_to_instructor(db_session, mock_notification_service):
    """create_review creates review, updates instructor average and dispatches notification."""
    notification_svc, gateway = mock_notification_service

    # Setup profiles and users
    student_user = User(id="student-1", email="student@test.com", password_hash="hash")
    instructor_user = User(id="instructor-1", email="instructor@test.com", password_hash="hash")
    db_session.add_all([student_user, instructor_user])
    db_session.flush()

    student_profile = StudentProfile(user_id="student-1", full_name="Student One")
    instructor_profile = InstructorProfile(
        user_id="instructor-1",
        full_name="Instructor One",
        rating_avg=0.0,
        rating_count=0,
    )
    db_session.add_all([student_profile, instructor_profile])
    db_session.flush()

    # Setup completed booking
    booking = Booking(
        id="booking-123",
        student_id="student-1",
        instructor_id="instructor-1",
        status="REALIZADA",
    )
    db_session.add(booking)
    db_session.flush()

    service = ReviewService(db_session, notification_service=notification_svc)
    
    review = service.create_review(
        booking_id="booking-123",
        reviewer_id="student-1",
        rating=5,
        comment="Excelente!",
        recipient_email="instructor@test.com"
    )

    assert review.id is not None
    assert review.booking_id == "booking-123"
    assert review.reviewer_id == "student-1"
    assert review.reviewed_id == "instructor-1"
    assert review.rating == 5
    assert review.comment == "Excelente!"

    # Verify instructor profile update
    db_session.refresh(instructor_profile)
    assert instructor_profile.rating_count == 1
    assert float(instructor_profile.rating_avg) == 5.0

    # Verify email dispatch
    assert len(gateway.sent_messages) == 1
    email = gateway.sent_messages[0]
    assert email["recipients"] == ["instructor@test.com"]
    assert "student-1" in email["body"]
    assert "5" in email["body"]


def test_create_review_rejects_non_realizada_booking(db_session):
    """create_review raises error if booking status is not REALIZADA."""
    booking = Booking(
        id="booking-123",
        student_id="student-1",
        instructor_id="instructor-1",
        status="CONFIRMADA",
    )
    db_session.add(booking)
    db_session.flush()

    service = ReviewService(db_session)
    
    with pytest.raises(ReviewStateError):
        service.create_review(
            booking_id="booking-123",
            reviewer_id="student-1",
            rating=5,
            comment="Ótimo",
        )


def test_create_review_rejects_duplicate_submission(db_session):
    """create_review raises error if reviewer already submitted a review for this booking."""
    booking = Booking(
        id="booking-123",
        student_id="student-1",
        instructor_id="instructor-1",
        status="REALIZADA",
    )
    db_session.add(booking)
    db_session.flush()

    # Pre-populate a review
    existing_review = Review(
        booking_id="booking-123",
        reviewer_id="student-1",
        reviewed_id="instructor-1",
        rating=4,
    )
    db_session.add(existing_review)
    db_session.flush()

    service = ReviewService(db_session)
    
    with pytest.raises(ReviewDuplicateError):
        service.create_review(
            booking_id="booking-123",
            reviewer_id="student-1",
            rating=5,
            comment="Outra",
        )


def test_create_review_rejects_unauthorized_user(db_session):
    """create_review raises error if reviewer is not part of the booking."""
    booking = Booking(
        id="booking-123",
        student_id="student-1",
        instructor_id="instructor-1",
        status="REALIZADA",
    )
    db_session.add(booking)
    db_session.flush()

    service = ReviewService(db_session)
    
    with pytest.raises(ReviewAccessError):
        service.create_review(
            booking_id="booking-123",
            reviewer_id="intruder-9",
            rating=5,
            comment="Invasor",
        )
