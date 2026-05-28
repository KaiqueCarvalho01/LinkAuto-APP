from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.booking import BookingStatus, transition_booking
from app.models.booking import Booking, BookingSlot
from app.models.slot import Slot
from app.services.booking_scheduler import BookingAutomationPort


class SqlAlchemyBookingAutomationPort(BookingAutomationPort):
    def __init__(self, db: Session):
        self._db = db

    def list_pending_expired(self, cutoff_utc: datetime) -> list[str]:
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
        from sqlalchemy import func

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

    def transition_to(
        self, booking_id: str, status: BookingStatus, reason: str
    ) -> None:
        booking = self._db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return
        new_status = transition_booking(
            BookingStatus(booking.status), status, admin_override=False
        )
        booking.status = new_status.value
        if status == BookingStatus.CANCELADA:
            booking.cancelled_by = "SISTEMA"
            booking.cancellation_reason = reason
        self._db.flush()
