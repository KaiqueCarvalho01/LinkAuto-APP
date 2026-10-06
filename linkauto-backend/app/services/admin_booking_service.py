from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.booking import BookingStatus, transition_booking
from app.models.booking import Booking

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AdminBookingService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def override_status(
        self,
        booking_id: str,
        target_status: str,
        reason: str,  # noqa: ARG002 - TODO: persist the admin's override reason
    ) -> Booking:
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
