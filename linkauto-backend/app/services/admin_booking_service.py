from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.booking import BookingStatus, transition_booking
from app.models.booking import Booking


class AdminBookingService:
    def __init__(self, db: Session):
        self._db = db

    def override_status(
        self, booking_id: str, target_status: str, reason: str
    ) -> Booking:
        if target_status not in (BookingStatus.REALIZADA.value, BookingStatus.CANCELADA.value):
            raise ValueError("Admin override target must be REALIZADA or CANCELADA")

        booking = self._db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")

        new_status = transition_booking(
            BookingStatus(booking.status),
            BookingStatus(target_status),
            admin_override=True,
        )
        booking.status = new_status.value
        self._db.flush()
        return booking
