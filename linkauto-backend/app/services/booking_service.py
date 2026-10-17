"""Booking lifecycle service (PENDENTE -> CONFIRMADA -> REALIZADA, or CANCELADA)."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlmodel import col, or_, select, update

from app.domain.booking import MIN_SLOTS_PER_BOOKING, BookingStatus, transition_booking
from app.models.booking import Booking, BookingSlot, CancelledBy
from app.models.slot import Slot, SlotStatus
from app.services.bookable_instructor import find_bookable_instructor
from app.services.booking_notifier import BookingNotifier
from app.services.penalty_service import PenaltyService

if TYPE_CHECKING:
    from collections.abc import Collection

    from sqlmodel import Session

    from app.services.notification_service import NotificationService

CANCELLATION_NOTICE_HOURS = 24


@dataclass(frozen=True, slots=True)
class BookingLocation:
    """Where the student wants to meet for the lesson."""

    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class BookingSide(StrEnum):
    """Which side of a booking a user is on: the student who booked or the instructor."""

    STUDENT = "student"
    INSTRUCTOR = "instructor"


class SlotValidationError(ValueError):
    """Raised when requested slots cannot be booked (RN02 or availability rules)."""


class BookingNotFoundError(LookupError):
    """Raised when the requested booking does not exist."""


class BookingAccessError(PermissionError):
    """Raised when a user attempts to operate on a booking they do not participate in."""


class InstructorUnavailableError(LookupError):
    """Raised when the instructor doesn't exist or can't be booked (not approved, inactive)."""


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
        self._notifier = BookingNotifier(db, notification_service)

    def create_booking(
        self,
        student_id: str,
        instructor_id: str,
        slot_ids: list[str],
        *,
        location: BookingLocation | None = None,
    ) -> Booking:
        """Create a PENDENTE booking over the given slots and reserve them.

        ``instructor_id`` may be an instructor slug. The instructor must be DETRAN-approved and
        active (RN01). The slots must be at least two consecutive, available slots of that
        instructor (RN02). The instructor is notified by email.

        Raises:
            PenalizedStudentError: If the student is currently penalized (RN04).
            InstructorUnavailableError: If the instructor isn't approved and active (RN01).
            SlotValidationError: If the slots violate RN02 or are unavailable.

        """
        # RN04: penalized student cannot book
        if self._penalty.is_penalized(student_id):
            msg = "Student is currently penalized and cannot create bookings"
            raise PenalizedStudentError(msg)

        # RN01: only approved, active instructors can be booked (slug or user ID)
        instructor = find_bookable_instructor(self._db, instructor_id)
        if instructor is None:
            msg = "Instructor not found or not accepting bookings"
            raise InstructorUnavailableError(msg)
        effective_instructor_id = instructor.user_id
        # A user with both roles must not book (and later review) their own lessons
        if effective_instructor_id == student_id:
            msg = "You cannot book your own slots"
            raise SlotValidationError(msg)

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

        # FR-021: e-mail the instructor
        self._notifier.booking_requested(booking)

        return booking

    def _get_bookable_slots(self, slot_ids: list[str], instructor_id: str) -> list[Slot]:
        # RN02: minimum 2 slots
        if len(slot_ids) < MIN_SLOTS_PER_BOOKING:
            msg = "Booking requires minimum 2 consecutive slots (RN02)"
            raise SlotValidationError(msg)

        slots = list(
            self._db.exec(
                select(Slot).where(col(Slot.id).in_(slot_ids)).order_by(col(Slot.starts_at))
            ).all()
        )

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

        Raises:
            BookingNotFoundError: If the booking does not exist.
            BookingAccessError: If the booking belongs to another instructor.
            BookingTransitionError: If the booking cannot transition to CONFIRMADA.

        """
        booking = self._get_booking_or_raise(booking_id)
        if booking.instructor_id != instructor_id:
            msg = "Only the instructor can confirm this booking"
            raise BookingAccessError(msg)

        new_status = transition_booking(BookingStatus(booking.status), BookingStatus.CONFIRMADA)
        booking.status = new_status.value
        booking.confirmed_at = datetime.now(UTC)
        self._db.flush()

        # FR-021: e-mail the student
        self._notifier.booking_confirmed(booking)

        return booking

    def cancel_booking(
        self,
        booking_id: str,
        user_id: str,
        reason: str | None = None,
    ) -> Booking:
        """Cancel a booking on behalf of one of its participants.

        The cancellation is attributed from the booking, not the caller's roles: to ALUNO when
        ``user_id`` is the booking's student, to INSTRUTOR when it is its instructor. So a user
        with both roles cancels each booking as the side they are on. When the student cancels
        less than 24 hours before the first slot, a 7-day penalty is applied (RN04).

        Raises:
            BookingNotFoundError: If the booking does not exist.
            BookingAccessError: If the user is not the booking's student or instructor.
            BookingTransitionError: If the booking is already in a terminal status.

        """
        booking = self._get_booking_or_raise(booking_id)
        if user_id == booking.student_id:
            cancelled_by = CancelledBy.ALUNO.value
        elif user_id == booking.instructor_id:
            cancelled_by = CancelledBy.INSTRUTOR.value
        else:
            msg = "Only a participant can cancel this booking"
            raise BookingAccessError(msg)
        return self._cancel(booking, cancelled_by, reason)

    def cancel_by_system(self, booking_id: str, reason: str) -> Booking | None:
        """Cancel a still-PENDENTE booking as SISTEMA (the 24h timeout).

        Releases its slots and notifies both participants. The booking is claimed with a
        conditional UPDATE (``status = PENDENTE``), so when two job runs overlap only one of
        them cancels it; the other gets ``None``, as it does for a booking that was confirmed
        or cancelled in the meantime or does not exist.
        """
        now = datetime.now(UTC)
        claimed = self._db.exec(
            update(Booking)
            .where(
                col(Booking.id) == booking_id,
                col(Booking.status) == BookingStatus.PENDENTE.value,
            )
            .values(
                status=BookingStatus.CANCELADA.value,
                cancelled_at=now,
                cancelled_by=CancelledBy.SISTEMA.value,
                cancellation_reason=reason,
            )
        )
        if claimed.rowcount != 1:
            return None
        booking = self._get_booking_or_raise(booking_id)
        self._db.refresh(booking)
        self._release_reserved_slots(booking)
        self._db.flush()
        self._notifier.booking_cancelled(booking)
        return booking

    def _cancel(self, booking: Booking, cancelled_by: str, reason: str | None) -> Booking:
        """Cancel the booking, release its reserved slots and notify the affected parties."""
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

        # FR-021: e-mail the other party (both for system cancellations)
        self._notifier.booking_cancelled(booking)

        return booking

    def _release_reserved_slots(self, booking: Booking) -> None:
        # Release reserved slots back to DISPONIVEL (D12: O(1) Batch Query Optimization)
        slot_ids = [link.slot_id for link in booking.slots]
        if not slot_ids:
            return
        for slot in self._db.exec(select(Slot).where(col(Slot.id).in_(slot_ids))).all():
            if slot.status == SlotStatus.RESERVADO.value:
                slot.status = SlotStatus.DISPONIVEL.value

    def _apply_late_cancellation_penalty(self, booking: Booking, now: datetime) -> None:
        # RN04: penalty if student cancels within 24h of first slot
        first_slot = self._db.exec(
            select(Slot)
            .join(BookingSlot, col(BookingSlot.slot_id) == col(Slot.id))
            .where(col(BookingSlot.booking_id) == booking.id)
            .order_by(col(Slot.starts_at))
        ).first()
        if not first_slot:
            return
        # Datetime columns use SQLModel's UTCDateTime, so loaded values are aware UTC
        if first_slot.starts_at - now < timedelta(hours=CANCELLATION_NOTICE_HOURS):
            self._penalty.apply_penalty(
                booking.student_id,
                reason=f"Cancelamento tardio (< 24h) do booking {booking.id} conforme RN04",
            )

    def get_booking(self, booking_id: str) -> Booking | None:
        """Return the booking with the given ID, or ``None`` if it does not exist."""
        return self._db.exec(select(Booking).where(col(Booking.id) == booking_id)).first()

    def list_bookings(
        self,
        user_id: str,
        sides: Collection[BookingSide],
        status_filter: str | None = None,
    ) -> list[Booking]:
        """Return the user's bookings on the given sides, newest first.

        ``BookingSide.STUDENT`` covers bookings the user made, ``BookingSide.INSTRUCTOR`` the
        bookings made with them; passing both returns the union.
        """
        conditions = []
        if BookingSide.STUDENT in sides:
            conditions.append(col(Booking.student_id) == user_id)
        if BookingSide.INSTRUCTOR in sides:
            conditions.append(col(Booking.instructor_id) == user_id)
        if not conditions:
            return []
        stmt = select(Booking).where(or_(*conditions))

        if status_filter:
            stmt = stmt.where(col(Booking.status) == status_filter)

        return list(self._db.exec(stmt.order_by(col(Booking.created_at).desc())).all())

    def _get_booking_or_raise(self, booking_id: str) -> Booking:
        booking = self.get_booking(booking_id)
        if not booking:
            msg = f"Booking {booking_id} not found"
            raise BookingNotFoundError(msg)
        return booking
