from typing import TYPE_CHECKING

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.booking import Booking
from app.models.booking_message import BookingMessage
from app.models.review import Review
from tests.factories import seed_participants

if TYPE_CHECKING:
    from sqlmodel import Session


def _seed_booking(db_session: Session) -> None:
    seed_participants(db_session, "student-uuid-placeholder", "instructor-uuid-placeholder")
    db_session.add(
        Booking(
            id="booking-uuid-placeholder",
            student_id="student-uuid-placeholder",
            instructor_id="instructor-uuid-placeholder",
        )
    )
    db_session.flush()


def test_booking_message_model_persists(db_session: Session) -> None:
    """BookingMessage model persists with required fields."""
    _seed_booking(db_session)
    message = BookingMessage(
        booking_id="booking-uuid-placeholder",
        sender_id="student-uuid-placeholder",
        content="Olá, esta é uma mensagem de teste.",
    )
    db_session.add(message)
    db_session.flush()

    assert message.id is not None
    assert message.content == "Olá, esta é uma mensagem de teste."
    assert message.created_at is not None


def test_review_model_persists_and_enforces_unicity(db_session: Session) -> None:
    """Review model persists and composition constraint restricts duplicate reviewer per booking."""
    _seed_booking(db_session)
    review1 = Review(
        booking_id="booking-uuid-placeholder",
        reviewer_id="student-uuid-placeholder",
        reviewed_id="instructor-uuid-placeholder",
        rating=5,
        comment="Excelente aula!",
    )
    db_session.add(review1)
    db_session.flush()

    assert review1.id is not None

    # Attempt duplicate review for the same booking and reviewer
    review2 = Review(
        booking_id="booking-uuid-placeholder",
        reviewer_id="student-uuid-placeholder",
        reviewed_id="instructor-uuid-placeholder",
        rating=4,
        comment="Outra avaliação",
    )
    db_session.add(review2)
    with pytest.raises(IntegrityError):
        db_session.flush()
