"""Admin overrides of booking statuses."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.booking import BookingStatus, transition_booking
from app.models.booking import Booking

if TYPE_CHECKING:
    from sqlmodel import Session


class AdminBookingService:
    """Let admins force a booking into a terminal status."""

    def __init__(self, db: Session) -> None:
        """Store the DB session used to load and update bookings."""
        self._db = db

    def override_status(
        self,
        booking_id: str,
        target_status: str,
        reason: str,  # noqa: ARG002 - TODO: persist the admin's override reason
    ) -> Booking:
        """Set the booking to REALIZADA or CANCELADA using the admin override rules.

        The admin override also allows switching between the two terminal statuses. The
        ``reason`` is accepted but not persisted yet. Raises ``ValueError`` for any other
        target status or an unknown booking, and ``BookingTransitionError`` if the
        transition is not allowed.
        """
        if target_status not in (BookingStatus.REALIZADA.value, BookingStatus.CANCELADA.value):
            msg = "Admin override target must be REALIZADA or CANCELADA"
            raise ValueError(msg)

        booking = self._db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            msg = f"Booking {booking_id} not found"
            raise ValueError(msg)

        new_status = transition_booking(
            BookingStatus(booking.status),
            BookingStatus(target_status),
            admin_override=True,
        )
        booking.status = new_status.value
        self._db.flush()
        return booking
