"""Admin overrides of booking statuses, recorded in an audit trail."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import col, select

from app.domain.booking import BookingStatus, transition_booking
from app.models.booking import Booking, BookingStatusOverride, CancelledBy
from app.models.slot import Slot, SlotStatus
from app.models.user import User
from app.services.booking_service import BookingNotFoundError
from app.services.notification_service import (
    NotificationEvent,
    NotificationPayload,
    NotificationService,
)

if TYPE_CHECKING:
    from sqlmodel import Session

OVERRIDE_TARGETS = (BookingStatus.REALIZADA.value, BookingStatus.CANCELADA.value)


class AdminBookingService:
    """Let admins force a booking into a terminal status."""

    def __init__(
        self, db: Session, notification_service: NotificationService | None = None
    ) -> None:
        """Store the DB session and the optional notification service."""
        self._db = db
        self._notification_service = notification_service

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
        booking.status = new_status.value
        now = datetime.now(UTC)

        cancelled = new_status == BookingStatus.CANCELADA
        if cancelled:
            booking.cancelled_at = now
            booking.cancelled_by = CancelledBy.ADMIN.value
            booking.cancellation_reason = reason
            self._release_future_reserved_slots(booking, now)
        else:
            booking.cancelled_at = None
            booking.cancelled_by = None
            booking.cancellation_reason = None

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
            self._notify_cancellation(booking, reason)
        return booking

    def _release_future_reserved_slots(self, booking: Booking, now: datetime) -> None:
        slot_ids = [link.slot_id for link in booking.slots]
        if not slot_ids:
            return
        for slot in self._db.exec(select(Slot).where(col(Slot.id).in_(slot_ids))).all():
            if slot.status == SlotStatus.RESERVADO.value and slot.starts_at > now:
                slot.status = SlotStatus.DISPONIVEL.value

    def _notify_cancellation(self, booking: Booking, reason: str) -> None:
        if self._notification_service is None:
            return
        recipients = []
        for user_id in (booking.student_id, booking.instructor_id):
            user = self._db.exec(select(User).where(col(User.id) == user_id)).first()
            if user:
                recipients.append(user.email)
        if not recipients:
            return
        self._notification_service.dispatch(
            NotificationPayload(
                event=NotificationEvent.BOOKING_CANCELLED,
                subject="Sua aula foi cancelada",
                body=(
                    f"O agendamento {booking.id} foi cancelado pela administração. Motivo: {reason}"
                ),
                recipients=recipients,
            )
        )
