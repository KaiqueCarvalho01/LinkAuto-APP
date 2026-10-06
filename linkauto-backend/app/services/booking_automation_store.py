"""SQLAlchemy persistence adapter for the booking scheduler."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func

from app.domain.booking import BookingStatus, transition_booking
from app.models.booking import Booking, BookingSlot
from app.models.slot import Slot
from app.models.user import User
from app.services.booking_scheduler import BookingAutomationPort

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.orm import Session


class SqlAlchemyBookingAutomationPort(BookingAutomationPort):
    """SQLAlchemy implementation of the booking scheduler's persistence port."""

    def __init__(self, db: Session) -> None:
        """Store the database session."""
        self._db = db

    def list_pending_expired(self, cutoff_utc: datetime) -> list[str]:
        """Return IDs of PENDENTE bookings created at or before ``cutoff_utc``."""
        bookings = (
            self._db.query(Booking)
            .filter(
                Booking.status == BookingStatus.PENDENTE.value,
                Booking.created_at <= cutoff_utc,
            )
            .all()
        )
        return [b.id for b in bookings]

    def list_confirmed_ready(self, cutoff_utc: datetime) -> list[str]:
        """Find confirmed bookings whose last slot ended before cutoff_utc."""
        results = (
            self._db.query(Booking.id)
            .join(BookingSlot, BookingSlot.booking_id == Booking.id)
            .join(Slot, Slot.id == BookingSlot.slot_id)
            .filter(Booking.status == BookingStatus.CONFIRMADA.value)
            .group_by(Booking.id)
            .having(func.max(Slot.ends_at) <= cutoff_utc)
            .all()
        )
        return [r[0] for r in results]

    def transition_to(self, booking_id: str, status: BookingStatus, reason: str) -> None:
        """Transition a booking to ``status``, ignoring unknown booking IDs.

        Cancellations are attributed to ``SISTEMA`` with ``reason`` as the cancellation reason.
        """
        booking = self._db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return
        new_status = transition_booking(BookingStatus(booking.status), status, admin_override=False)
        booking.status = new_status.value
        if status == BookingStatus.CANCELADA:
            booking.cancelled_by = "SISTEMA"
            booking.cancellation_reason = reason
        self._db.flush()

    def list_unreminded_upcoming(self, start_cutoff: datetime, end_cutoff: datetime) -> list[str]:
        """Return IDs of unreminded CONFIRMADA bookings whose first slot starts in the window."""
        results = (
            self._db.query(Booking.id)
            .join(BookingSlot, BookingSlot.booking_id == Booking.id)
            .join(Slot, Slot.id == BookingSlot.slot_id)
            .filter(
                Booking.status == BookingStatus.CONFIRMADA.value,
                Booking.reminder_sent.is_(False),
            )
            .group_by(Booking.id)
            .having(func.min(Slot.starts_at) >= start_cutoff)
            .having(func.min(Slot.starts_at) <= end_cutoff)
            .all()
        )
        return [r[0] for r in results]

    def mark_reminder_sent(self, booking_id: str) -> None:
        """Flag the booking's lesson reminder as sent, if the booking exists."""
        booking = self._db.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            booking.reminder_sent = True
            self._db.flush()

    def get_booking_emails(self, booking_id: str) -> tuple[str | None, str | None]:
        """Return the student and instructor emails of a booking, ``None`` when unknown."""
        booking = self._db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return None, None

        student = self._db.query(User).filter(User.id == booking.student_id).first()
        instructor = self._db.query(User).filter(User.id == booking.instructor_id).first()

        student_email = student.email if student else None
        instructor_email = instructor.email if instructor else None
        return student_email, instructor_email
