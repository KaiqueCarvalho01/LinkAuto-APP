"""Reviews are split by side, and the instructor's cached rating follows the source (#74)."""

from typing import TYPE_CHECKING

from app.models import Booking, InstructorProfile, StudentProfile
from app.services.admin_booking_service import AdminBookingService
from app.services.public_profile_service import PublicProfileService
from app.services.review_service import ReviewService
from tests.factories import seed_admin, seed_instructor, seed_student

if TYPE_CHECKING:
    from sqlmodel import Session


def _lesson(db: Session, student_id: str, instructor_id: str) -> str:
    booking = Booking(student_id=student_id, instructor_id=instructor_id, status="REALIZADA")
    db.add(booking)
    db.flush()
    return booking.id


def _profile(db: Session, user_id: str) -> InstructorProfile:
    profile = db.get(InstructorProfile, user_id)
    assert profile is not None
    db.refresh(profile)
    return profile


def test_reviews_received_as_student_stay_off_the_instructor_profile(
    db_session: Session,
) -> None:
    # X teaches (instructor profile) and also takes lessons from Y (student profile)
    seed_instructor(db_session, "x", full_name="Xavier")
    seed_student(db_session, "x", full_name="Xavier")
    seed_instructor(db_session, "y", full_name="Yara")
    seed_student(db_session, "s", full_name="Sofia")
    taught = _lesson(db_session, "s", "x")
    took = _lesson(db_session, "x", "y")
    reviews = ReviewService(db_session)
    reviews.create_review(taught, "s", 5, "Ótimo instrutor")
    reviews.create_review(took, "y", 1, "Aluno atrasado")

    service = PublicProfileService(db_session)
    instructor_page = service.get_public_instructor(_profile(db_session, "x").slug)
    student = db_session.get(StudentProfile, "x")
    assert student is not None
    student_page = service.get_public_student(student.slug)

    assert [r.comment for r in instructor_page.reviews] == ["Ótimo instrutor"]
    assert instructor_page.rating_count == 1
    assert [r.comment for r in student_page.reviews] == ["Aluno atrasado"]
    assert student_page.rating_avg == 1.0


def test_rating_is_recomputed_from_the_reviews(db_session: Session) -> None:
    seed_instructor(db_session, "i")
    seed_student(db_session, "a")
    seed_student(db_session, "b")
    profile = _profile(db_session, "i")
    # A cached value that drifted (e.g. a lost update from two concurrent reviews)
    profile.rating_avg, profile.rating_count = 5.0, 7
    db_session.flush()
    reviews = ReviewService(db_session)

    reviews.create_review(_lesson(db_session, "a", "i"), "a", 5)
    reviews.create_review(_lesson(db_session, "b", "i"), "b", 1)

    profile = _profile(db_session, "i")
    assert (profile.rating_avg, profile.rating_count) == (3.0, 2)


def test_cancelling_a_realized_lesson_removes_its_review_from_the_rating(
    db_session: Session,
) -> None:
    seed_instructor(db_session, "i")
    seed_student(db_session, "a")
    seed_admin(db_session)
    booking_id = _lesson(db_session, "a", "i")
    ReviewService(db_session).create_review(booking_id, "a", 5, "Aula que não houve")
    assert _profile(db_session, "i").rating_count == 1

    AdminBookingService(db_session).override_status(
        booking_id, "CANCELADA", "Aula não aconteceu", admin_id="admin-1"
    )

    profile = _profile(db_session, "i")
    assert (profile.rating_avg, profile.rating_count) == (0.0, 0)
    page = PublicProfileService(db_session).get_public_instructor(profile.slug)
    assert page.reviews == []
