"""SQLAlchemy persistence adapter for the booking scheduler."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from sqlalchemy import func
from sqlmodel import col, select

from app.domain.booking import BookingStatus, transition_booking
from app.models.booking import Booking, BookingSlot
from app.models.slot import Slot
from app.models.user import User
from app.services.booking_scheduler import BookingAutomationPort

if TYPE_CHECKING:
    from datetime import datetime

    from sqlmodel import Session


class SqlAlchemyBookingAutomationPort(BookingAutomationPort):
    """SQLAlchemy implementation of the booking scheduler's persistence port."""

    def __init__(self, db: Session) -> None:
        """Store the database session."""
        self._db = db

    @override
    def list_pending_expired(self, cutoff_utc: datetime) -> list[str]:
        """Return IDs of PENDENTE bookings created at or before ``cutoff_utc``."""
        bookings = self._db.exec(
            select(Booking).where(
                col(Booking.status) == BookingStatus.PENDENTE.value,
                col(Booking.created_at) <= cutoff_utc,
            )
        ).all()
        return [b.id for b in bookings]

    @override
    def list_confirmed_ready(self, cutoff_utc: datetime) -> list[str]:
        """Find confirmed bookings whose last slot ended before cutoff_utc."""
        results = self._db.exec(
            select(Booking.id)
            .join(BookingSlot, col(BookingSlot.booking_id) == col(Booking.id))
            .join(Slot, col(Slot.id) == col(BookingSlot.slot_id))
            .where(col(Booking.status) == BookingStatus.CONFIRMADA.value)
            .group_by(col(Booking.id))
            .having(func.max(col(Slot.ends_at)) <= cutoff_utc)
        ).all()
        return list(results)

    @override
    def transition_to(self, booking_id: str, status: BookingStatus, reason: str) -> None:
        """Transition a booking to ``status``, ignoring unknown booking IDs.

        Cancellations are attributed to ``SISTEMA`` with ``reason`` as the cancellation reason.
        """
        booking = self._db.exec(select(Booking).where(col(Booking.id) == booking_id)).first()
        if not booking:
            return
        new_status = transition_booking(BookingStatus(booking.status), status, admin_override=False)
        booking.status = new_status.value
        if status == BookingStatus.CANCELADA:
            booking.cancelled_by = "SISTEMA"
            booking.cancellation_reason = reason
        self._db.flush()

    @override
    def list_unreminded_upcoming(self, start_cutoff: datetime, end_cutoff: datetime) -> list[str]:
        """Return IDs of unreminded CONFIRMADA bookings whose first slot starts in the window."""
        results = self._db.exec(
            select(Booking.id)
            .join(BookingSlot, col(BookingSlot.booking_id) == col(Booking.id))
            .join(Slot, col(Slot.id) == col(BookingSlot.slot_id))
            .where(
                col(Booking.status) == BookingStatus.CONFIRMADA.value,
                col(Booking.reminder_sent).is_(False),
            )
            .group_by(col(Booking.id))
            .having(func.min(col(Slot.starts_at)) >= start_cutoff)
            .having(func.min(col(Slot.starts_at)) <= end_cutoff)
        ).all()
        return list(results)

    @override
    def mark_reminder_sent(self, booking_id: str) -> None:
        """Flag the booking's lesson reminder as sent, if the booking exists."""
        booking = self._db.exec(select(Booking).where(col(Booking.id) == booking_id)).first()
        if booking:
            booking.reminder_sent = True
            self._db.flush()

    @override
    def get_booking_emails(self, booking_id: str) -> tuple[str | None, str | None]:
        """Return the student and instructor emails of a booking, ``None`` when unknown."""
        booking = self._db.exec(select(Booking).where(col(Booking.id) == booking_id)).first()
        if not booking:
            return None, None

        student = self._db.exec(select(User).where(col(User.id) == booking.student_id)).first()
        instructor = self._db.exec(
            select(User).where(col(User.id) == booking.instructor_id)
        ).first()

        student_email = student.email if student else None
        instructor_email = instructor.email if instructor else None
        return student_email, instructor_email
