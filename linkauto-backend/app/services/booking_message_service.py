from __future__ import annotations

import logging
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.booking_message import BookingMessage
from app.services.notification_service import NotificationService, NotificationPayload, NotificationEvent

logger = logging.getLogger(__name__)


class BookingMessageAccessError(ValueError):
    pass


class BookingMessageService:
    def __init__(
        self,
        db: Session,
        notification_service: NotificationService | None = None,
    ) -> None:
        self._db = db
        self._notification_service = notification_service

    def send_message(
        self,
        booking_id: str,
        sender_id: str,
        content: str,
        sender_email: str | None = None,
        recipient_email: str | None = None,
    ) -> BookingMessage:
        # Fetch booking to check existence and authorization
        booking = self._db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")

        # Validate access control: sender must be student or instructor
        if sender_id not in (booking.student_id, booking.instructor_id):
            logger.warning(
                f"Access denied: User {sender_id} is not authorized to message on booking {booking_id}"
            )
            raise BookingMessageAccessError("You are not a participant in this booking")

        # Create the message
        message = BookingMessage(
            booking_id=booking_id,
            sender_id=sender_id,
            content=content,
        )
        self._db.add(message)
        self._db.flush()

        # Send notification to the opposite party
        if self._notification_service and recipient_email:
            opposing_role = "ALUNO" if sender_id == booking.instructor_id else "INSTRUTOR"
            
            self._notification_service.dispatch(
                NotificationPayload(
                    event=NotificationEvent.NEW_BOOKING_MESSAGE,
                    subject="Nova mensagem recebida",
                    body=f"Você recebeu uma nova mensagem de {sender_id} ({opposing_role}): '{content}'",
                    recipients=[recipient_email],
                )
            )

        return message

    def list_messages(
        self,
        booking_id: str,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> list[BookingMessage]:
        # Fetch booking to check existence and authorization
        booking = self._db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")

        # Validate access control
        if user_id not in (booking.student_id, booking.instructor_id):
            logger.warning(
                f"Access denied: User {user_id} is not authorized to list messages on booking {booking_id}"
            )
            raise BookingMessageAccessError("You are not a participant in this booking")

        # Query messages chronologically
        offset = (page - 1) * page_size
        return (
            self._db.query(BookingMessage)
            .filter(BookingMessage.booking_id == booking_id)
            .order_by(BookingMessage.created_at.asc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
