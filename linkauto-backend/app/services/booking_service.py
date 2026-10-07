"""Booking lifecycle service (PENDENTE -> CONFIRMADA -> REALIZADA, or CANCELADA)."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.domain.booking import MIN_SLOTS_PER_BOOKING, BookingStatus, transition_booking
from app.models.booking import Booking, BookingSlot, CancelledBy
from app.models.slot import Slot, SlotStatus
from app.models.user import InstructorProfile, User
from app.services.notification_service import (
    NotificationEvent,
    NotificationPayload,
    NotificationService,
)
from app.services.penalty_service import PenaltyService

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

CANCELLATION_NOTICE_HOURS = 24


@dataclass(frozen=True, slots=True)
class BookingLocation:
    """Where the student wants to meet for the lesson."""

    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class SlotValidationError(ValueError):
    """Raised when requested slots cannot be booked (RN02 or availability rules)."""


class BookingAccessError(PermissionError):
    """Raised when a user attempts to operate on a booking they do not participate in."""


class PenalizedStudentError(ValueError):
    """Raised when a student under an RN04 penalty tries to create a booking."""


class BookingService:
    """Create, confirm, cancel and query bookings, enforcing RN02 and RN04."""

    def __init__(
        self,
        db: Session,
        notification_service: NotificationService | None = None,
    ) -> None:
        """Store the database session, a penalty service and optional notification service."""
        self._db = db
        self._penalty = PenaltyService(db)
        self._notification_service = notification_service

    def create_booking(
        self,
        student_id: str,
        instructor_id: str,
        slot_ids: list[str],
        *,
        location: BookingLocation | None = None,
    ) -> Booking:
        """Create a PENDENTE booking over the given slots and reserve them.

        ``instructor_id`` may be an instructor slug. The slots must be at least two consecutive,
        available slots of that instructor (RN02). The instructor is notified by email.

        Raises:
            PenalizedStudentError: If the student is currently penalized (RN04).
            SlotValidationError: If the slots violate RN02 or are unavailable.

        """
        # RN04: penalized student cannot book
        if self._penalty.is_penalized(student_id):
            msg = "Student is currently penalized and cannot create bookings"
            raise PenalizedStudentError(msg)

        # Resolve instructor slug if necessary

        inst_prof = (
            self._db.query(InstructorProfile)
            .filter(InstructorProfile.slug == instructor_id)
            .first()
        )
        effective_instructor_id = inst_prof.user_id if inst_prof else instructor_id

        slots = self._get_bookable_slots(slot_ids, effective_instructor_id)

        # Reserve slots atomically (first-write-wins)
        for slot in slots:
            slot.status = SlotStatus.RESERVADO.value
        self._db.flush()

        # Create booking
        booking = Booking(
            student_id=student_id,
            instructor_id=effective_instructor_id,
            status=BookingStatus.PENDENTE.value,
            location_description=location.description if location else None,
            latitude=location.latitude if location else None,
            longitude=location.longitude if location else None,
        )
        self._db.add(booking)
        self._db.flush()

        # Link slots to booking
        for slot in slots:
            link = BookingSlot(booking_id=booking.id, slot_id=slot.id)
            self._db.add(link)
        self._db.flush()

        # FR-021: trigger email notification to instructor
        instructor_user = self._db.query(User).filter(User.id == instructor_id).first()
        if instructor_user and self._notification_service:
            self._notification_service.dispatch(
                NotificationPayload(
                    event=NotificationEvent.NEW_PENDING_BOOKING,
                    subject="Nova reserva pendente",
                    body=f"Você tem um novo agendamento pendente criado pelo aluno {student_id}.",
                    recipients=[instructor_user.email],
                )
            )

        return booking

    def _get_bookable_slots(self, slot_ids: list[str], instructor_id: str) -> list[Slot]:
        # RN02: minimum 2 slots
        if len(slot_ids) < MIN_SLOTS_PER_BOOKING:
            msg = "Booking requires minimum 2 consecutive slots (RN02)"
            raise SlotValidationError(msg)

        slots = self._db.query(Slot).filter(Slot.id.in_(slot_ids)).order_by(Slot.starts_at).all()

        if len(slots) != len(slot_ids):
            msg = "One or more slot IDs not found"
            raise SlotValidationError(msg)

        # All slots must belong to same instructor
        if not all(s.instructor_id == instructor_id for s in slots):
            msg = "All slots must belong to the specified instructor"
            raise SlotValidationError(msg)

        # All slots must be available
        unavailable = [s for s in slots if s.status != SlotStatus.DISPONIVEL.value]
        if unavailable:
            msg = f"Slots not available: {[s.id for s in unavailable]}"
            raise SlotValidationError(msg)

        # RN02: slots must be consecutive (each starts when previous ends)
        for previous, current in itertools.pairwise(slots):
            if current.starts_at != previous.ends_at:
                msg = "Slots must be consecutive — each slot must start when the previous ends"
                raise SlotValidationError(msg)

        return slots

    def confirm_booking(self, booking_id: str, instructor_id: str) -> Booking:
        """Move a PENDENTE booking to CONFIRMADA and notify the student by email.

        Raises ``ValueError`` if the booking does not exist, belongs to another instructor or
        cannot transition to CONFIRMADA.
        """
        booking = self._get_booking_or_raise(booking_id)
        if booking.instructor_id != instructor_id:
            msg = "Only the instructor can confirm this booking"
            raise ValueError(msg)

        new_status = transition_booking(BookingStatus(booking.status), BookingStatus.CONFIRMADA)
        booking.status = new_status.value
        booking.confirmed_at = datetime.now(UTC)
        self._db.flush()

        # FR-021: trigger email notification to student
        student_user = self._db.query(User).filter(User.id == booking.student_id).first()
        if student_user and self._notification_service:
            self._notification_service.dispatch(
                NotificationPayload(
                    event=NotificationEvent.BOOKING_CONFIRMED,
                    subject="Sua aula foi confirmada",
                    body=(
                        f"Sua solicitação de agendamento {booking_id} foi confirmada pelo "
                        f"instrutor {instructor_id}."
                    ),
                    recipients=[student_user.email],
                )
            )

        return booking

    def cancel_booking(
        self,
        booking_id: str,
        user_id: str,
        cancelled_by: str,
        reason: str | None = None,
    ) -> Booking:
        """Cancel a booking, release its reserved slots and notify the affected parties.

        When the student cancels less than 24 hours before the first slot, a 7-day penalty is
        applied (RN04). Raises ``ValueError`` if the booking does not exist or cannot be cancelled.
        """
        booking = self._get_booking_or_raise(booking_id)
        participant_id = {
            CancelledBy.ALUNO.value: booking.student_id,
            CancelledBy.INSTRUTOR.value: booking.instructor_id,
        }.get(cancelled_by)
        if participant_id is not None and participant_id != user_id:
            msg = "Only a participant can cancel this booking"
            raise BookingAccessError(msg)

        new_status = transition_booking(BookingStatus(booking.status), BookingStatus.CANCELADA)
        now = datetime.now(UTC)

        booking.status = new_status.value
        booking.cancelled_at = now
        booking.cancelled_by = cancelled_by
        booking.cancellation_reason = reason

        self._release_reserved_slots(booking)
        if cancelled_by == CancelledBy.ALUNO.value:
            self._apply_late_cancellation_penalty(booking, now)
        self._db.flush()

        # FR-021: trigger email notification to student and/or instructor
        recipients = self._cancellation_recipients(booking, cancelled_by)
        if recipients and self._notification_service:
            self._notification_service.dispatch(
                NotificationPayload(
                    event=NotificationEvent.BOOKING_CANCELLED,
                    subject="Sua aula foi cancelada",
                    body=(
                        f"O agendamento {booking_id} foi cancelado por {cancelled_by}. Motivo: "
                        f"{reason or ''}"
                    ),
                    recipients=recipients,
                )
            )

        return booking

    def _release_reserved_slots(self, booking: Booking) -> None:
        # Release reserved slots back to DISPONIVEL (D12: O(1) Batch Query Optimization)
        slot_ids = [link.slot_id for link in booking.slots]
        if not slot_ids:
            return
        for slot in self._db.query(Slot).filter(Slot.id.in_(slot_ids)).all():
            if slot.status == SlotStatus.RESERVADO.value:
                slot.status = SlotStatus.DISPONIVEL.value

    def _apply_late_cancellation_penalty(self, booking: Booking, now: datetime) -> None:
        # RN04: penalty if student cancels within 24h of first slot
        first_slot = (
            self._db.query(Slot)
            .join(BookingSlot, BookingSlot.slot_id == Slot.id)
            .filter(BookingSlot.booking_id == booking.id)
            .order_by(Slot.starts_at)
            .first()
        )
        if not first_slot:
            return
        first_slot_starts = first_slot.starts_at
        if first_slot_starts.tzinfo is None:
            first_slot_starts = first_slot_starts.replace(tzinfo=UTC)
        if first_slot_starts - now < timedelta(hours=CANCELLATION_NOTICE_HOURS):
            self._penalty.apply_penalty(
                booking.student_id,
                reason=f"Cancelamento tardio (< 24h) do booking {booking.id} conforme RN04",
            )

    def _cancellation_recipients(self, booking: Booking, cancelled_by: str) -> list[str]:
        # Notify the other party; system cancellations (timeouts) notify both
        if cancelled_by == CancelledBy.ALUNO.value:
            user_ids = [booking.instructor_id]
        elif cancelled_by == CancelledBy.INSTRUTOR.value:
            user_ids = [booking.student_id]
        else:
            user_ids = [booking.student_id, booking.instructor_id]
        recipients = []
        for user_id in user_ids:
            user = self._db.query(User).filter(User.id == user_id).first()
            if user:
                recipients.append(user.email)
        return recipients

    def get_booking(self, booking_id: str) -> Booking | None:
        """Return the booking with the given ID, or ``None`` if it does not exist."""
        return self._db.query(Booking).filter(Booking.id == booking_id).first()

    def list_bookings(
        self,
        user_id: str,
        role: str,
        status_filter: str | None = None,
    ) -> list[Booking]:
        """Return the user's bookings as student (``ALUNO``) or instructor, newest first."""
        if role == "ALUNO":
            query = self._db.query(Booking).filter(Booking.student_id == user_id)
        else:
            query = self._db.query(Booking).filter(Booking.instructor_id == user_id)

        if status_filter:
            query = query.filter(Booking.status == status_filter)

        return query.order_by(Booking.created_at.desc()).all()

    def _get_booking_or_raise(self, booking_id: str) -> Booking:
        booking = self.get_booking(booking_id)
        if not booking:
            msg = f"Booking {booking_id} not found"
            raise ValueError(msg)
        return booking
