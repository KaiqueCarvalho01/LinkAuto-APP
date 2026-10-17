"""SQLAlchemy persistence adapter for the booking scheduler."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from sqlalchemy import func
from sqlmodel import col, select, update

from app.domain.booking import BookingStatus
from app.models.booking import Booking, BookingSlot
from app.models.slot import Slot
from app.services.booking_scheduler import BookingAutomationPort
from app.services.booking_service import BookingService

if TYPE_CHECKING:
    from datetime import datetime

    from sqlmodel import Session

    from app.services.notification_service import NotificationService


class SqlAlchemyBookingAutomationPort(BookingAutomationPort):
    """SQLAlchemy implementation of the booking scheduler's persistence port.

    Each booking is handled in its own SAVEPOINT, so a failure rolls back only that booking.
    Methods flush; the caller commits the run.
    """

    def __init__(
        self, db: Session, notification_service: NotificationService | None = None
    ) -> None:
        """Store the database session and the service that notifies timeout cancellations."""
        self._db = db
        self._bookings = BookingService(db, notification_service=notification_service)

    @override
    def list_pending_expired(self, cutoff_utc: datetime) -> list[str]:
        """Return IDs of PENDENTE bookings created at or before ``cutoff_utc``."""
        return list(
            self._db.exec(
                select(Booking.id).where(
                    col(Booking.status) == BookingStatus.PENDENTE.value,
                    col(Booking.created_at) <= cutoff_utc,
                )
            ).all()
        )

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
    def cancel_expired(self, booking_id: str, reason: str) -> bool:
        """Cancel the booking as SISTEMA if it is still PENDENTE (see ``cancel_by_system``)."""
        with self._db.begin_nested():
            return self._bookings.cancel_by_system(booking_id, reason) is not None

    @override
    def complete(self, booking_id: str) -> bool:
        """Move the booking to REALIZADA if it is still CONFIRMADA (conditional UPDATE)."""
        with self._db.begin_nested():
            result = self._db.exec(
                update(Booking)
                .where(
                    col(Booking.id) == booking_id,
                    col(Booking.status) == BookingStatus.CONFIRMADA.value,
                )
                .values(status=BookingStatus.REALIZADA.value)
            )
            return result.rowcount == 1

    @override
    def claim_reminder(self, booking_id: str) -> bool:
        """Flag the reminder as sent if it is still unsent (conditional UPDATE)."""
        with self._db.begin_nested():
            result = self._db.exec(
                update(Booking)
                .where(
                    col(Booking.id) == booking_id,
                    col(Booking.status) == BookingStatus.CONFIRMADA.value,
                    col(Booking.reminder_sent).is_(False),
                )
                .values(reminder_sent=True)
            )
            return result.rowcount == 1
