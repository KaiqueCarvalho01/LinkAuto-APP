"""Chat messages exchanged between the student and instructor of a booking."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlmodel import col, select

from app.models.booking import Booking
from app.models.booking_message import BookingMessage
from app.services.booking_notifier import BookingNotifier

if TYPE_CHECKING:
    from sqlmodel import Session

    from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class BookingMessageAccessError(ValueError):
    """Raised when a user who is not the booking's student or instructor accesses its chat."""


class BookingMessageService:
    """Send and list booking messages, restricted to the booking's participants."""

    def __init__(
        self,
        db: Session,
        notification_service: NotificationService | None = None,
    ) -> None:
        """Store the DB session and the optional service used to notify the recipient."""
        self._db = db
        self._notifier = BookingNotifier(db, notification_service)

    def send_message(
        self,
        booking_id: str,
        sender_id: str,
        content: str,
    ) -> BookingMessage:
        """Persist a message on the booking and notify the other participant by e-mail.

        Raises ``ValueError`` if the booking does not exist and
        ``BookingMessageAccessError`` if the sender is not a participant.
        """
        # Fetch booking to check existence and authorization
        booking = self._db.exec(select(Booking).where(col(Booking.id) == booking_id)).first()
        if not booking:
            msg = f"Booking {booking_id} not found"
            raise ValueError(msg)

        # Validate access control: sender must be student or instructor
        if sender_id not in (booking.student_id, booking.instructor_id):
            logger.warning(
                "Access denied: User %s is not authorized to message on booking %s",
                sender_id,
                booking_id,
            )
            msg = "You are not a participant in this booking"
            raise BookingMessageAccessError(msg)

        # Create the message
        message = BookingMessage(
            booking_id=booking_id,
            sender_id=sender_id,
            content=content,
        )
        self._db.add(message)
        self._db.flush()

        # E-mail the other participant
        self._notifier.message_received(booking, sender_id=sender_id, content=content)

        return message

    def list_messages(
        self,
        booking_id: str,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> list[BookingMessage]:
        """Return a page of the booking's messages, oldest first.

        Raises ``ValueError`` if the booking does not exist and ``BookingMessageAccessError``
        if the user is not a participant.
        """
        # Fetch booking to check existence and authorization
        booking = self._db.exec(select(Booking).where(col(Booking.id) == booking_id)).first()
        if not booking:
            msg = f"Booking {booking_id} not found"
            raise ValueError(msg)

        # Validate access control
        if user_id not in (booking.student_id, booking.instructor_id):
            logger.warning(
                "Access denied: User %s is not authorized to list messages on booking %s",
                user_id,
                booking_id,
            )
            msg = "You are not a participant in this booking"
            raise BookingMessageAccessError(msg)

        # Query messages chronologically
        offset = (page - 1) * page_size
        return list(
            self._db.exec(
                select(BookingMessage)
                .where(col(BookingMessage.booking_id) == booking_id)
                .order_by(col(BookingMessage.created_at).asc())
                .offset(offset)
                .limit(page_size)
            ).all()
        )
