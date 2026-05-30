import pytest
from sqlalchemy.exc import IntegrityError

from app.models.booking_message import BookingMessage
from app.models.review import Review


def test_booking_message_model_persists(db_session):
    """BookingMessage model persists with required fields."""
    message = BookingMessage(
        booking_id="booking-uuid-placeholder",
        sender_id="sender-uuid-placeholder",
        content="Olá, esta é uma mensagem de teste.",
    )
    db_session.add(message)
    db_session.flush()

    assert message.id is not None
    assert message.content == "Olá, esta é uma mensagem de teste."
    assert message.created_at is not None


def test_review_model_persists_and_enforces_unicity(db_session):
    """Review model persists and composition constraint restricts duplicate reviewer per booking."""
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
