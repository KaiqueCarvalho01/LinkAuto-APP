from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.models.booking import Booking
from app.models.booking_message import BookingMessage
from app.services.notification_service import (
    NotificationEvent,
    NotificationPayload,
    NotificationService,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

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
        return (
            self._db.query(BookingMessage)
            .filter(BookingMessage.booking_id == booking_id)
            .order_by(BookingMessage.created_at.asc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
