"""Admin overrides of booking statuses, recorded in an audit trail."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import col, select

from app.domain.booking import BookingStatus, transition_booking
from app.models.booking import Booking, BookingStatusOverride, CancelledBy
from app.services.booking_notifier import BookingNotifier
from app.services.booking_service import (
    BookingNotFoundError,
    claim_status_change,
    release_booking_slots,
)
from app.services.review_service import refresh_instructor_rating

if TYPE_CHECKING:
    from sqlmodel import Session

    from app.services.notification_service import NotificationService

OVERRIDE_TARGETS = (BookingStatus.REALIZADA.value, BookingStatus.CANCELADA.value)


class AdminBookingService:
    """Let admins force a booking into a terminal status."""

    def __init__(
        self, db: Session, notification_service: NotificationService | None = None
    ) -> None:
        """Store the DB session and the optional notification service."""
        self._db = db
        self._notifier = BookingNotifier(db, notification_service)

    def override_status(
        self, booking_id: str, target_status: str, reason: str, *, admin_id: str
    ) -> Booking:
        """Set the booking to REALIZADA or CANCELADA using the admin override rules.

        The admin override also allows switching between the two terminal statuses. Every
        override is stored in ``booking_status_overrides`` (admin, from/to status, reason,
        time). Overriding to CANCELADA also fills the cancellation fields with
        ``cancelled_by=ADMIN``, releases the booking's future reserved slots and notifies
        both participants; moving away from CANCELADA clears the cancellation fields.

        Raises:
            ValueError: If the target status is not REALIZADA or CANCELADA.
            BookingNotFoundError: If the booking does not exist.
            BookingTransitionError: If the transition is not allowed.

        """
        if target_status not in OVERRIDE_TARGETS:
            msg = "Admin override target must be REALIZADA or CANCELADA"
            raise ValueError(msg)

        booking = self._db.exec(select(Booking).where(col(Booking.id) == booking_id)).first()
        if not booking:
            msg = f"Booking {booking_id} not found"
            raise BookingNotFoundError(msg)

        previous_status = booking.status
        new_status = transition_booking(
            BookingStatus(previous_status),
            BookingStatus(target_status),
            admin_override=True,
        )
        now = datetime.now(UTC)

        cancelled = new_status == BookingStatus.CANCELADA
        claim_status_change(
            self._db,
            booking,
            previous_status,
            status=new_status.value,
            cancelled_at=now if cancelled else None,
            cancelled_by=CancelledBy.ADMIN.value if cancelled else None,
            cancellation_reason=reason if cancelled else None,
        )
        if cancelled:
            self._release_future_reserved_slots(booking, now)
        # Only REALIZADA lessons count towards the instructor's rating
        if BookingStatus.REALIZADA.value in (previous_status, new_status.value):
            refresh_instructor_rating(self._db, booking.instructor_id)

        self._db.add(
            BookingStatusOverride(
                booking_id=booking.id,
                admin_id=admin_id,
                from_status=previous_status,
                to_status=new_status.value,
                reason=reason,
            )
        )
        self._db.flush()

        if cancelled and previous_status != BookingStatus.CANCELADA.value:
            self._notifier.booking_cancelled(booking)
        return booking

    def _release_future_reserved_slots(self, booking: Booking, now: datetime) -> None:
        release_booking_slots(self._db, booking, starting_after=now)
