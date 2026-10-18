"""Management of instructors' availability slots."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import and_
from sqlmodel import col, select

from app.models.booking import BookingSlot
from app.models.slot import Slot, SlotStatus
from app.services.bookable_instructor import find_bookable_instructor

if TYPE_CHECKING:
    from sqlmodel import Session


class SlotOverlapError(ValueError):
    """Raised when a new slot overlaps an existing slot of the same instructor."""


class SlotService:
    """Manage instructors' availability slots."""

    def __init__(self, db: Session) -> None:
        """Store the database session."""
        self._db = db

    def create_slot(
        self,
        instructor_id: str,
        starts_at: datetime,
        ends_at: datetime,
    ) -> Slot:
        """Create a DISPONIVEL slot, raising ``SlotOverlapError`` if it overlaps an existing one.

        Removed (BLOQUEADO) slots don't count, so a removed hour can be opened again.
        """
        overlap = self._db.exec(
            select(Slot).where(
                and_(
                    col(Slot.instructor_id) == instructor_id,
                    col(Slot.status) != SlotStatus.BLOQUEADO.value,
                    col(Slot.starts_at) < ends_at,
                    col(Slot.ends_at) > starts_at,
                )
            )
        ).first()
        if overlap:
            msg = (
                f"Slot overlaps with existing slot {overlap.id} "
                f"({overlap.starts_at} - {overlap.ends_at})"
            )
            raise SlotOverlapError(msg)

        slot = Slot(
            instructor_id=instructor_id,
            starts_at=starts_at,
            ends_at=ends_at,
            status=SlotStatus.DISPONIVEL.value,
        )
        self._db.add(slot)
        self._db.flush()
        return slot

    def list_slots(
        self,
        instructor_id: str,
        status: SlotStatus | None = None,
    ) -> list[Slot]:
        """Return an instructor's slots ordered by start time, optionally filtered by status.

        Removed (BLOQUEADO) slots are left out unless asked for explicitly.
        """
        stmt = select(Slot).where(col(Slot.instructor_id) == instructor_id)
        if status:
            stmt = stmt.where(col(Slot.status) == status.value)
        else:
            stmt = stmt.where(col(Slot.status) != SlotStatus.BLOQUEADO.value)
        return list(self._db.exec(stmt.order_by(col(Slot.starts_at))).all())

    def list_public_slots(self, instructor_ref: str) -> list[Slot]:
        """Return the slots of a bookable instructor, identified by public slug or user ID.

        Only slots that haven't started yet are returned: past ones can't be booked. Raises
        ``LookupError`` when the instructor doesn't exist or isn't DETRAN-approved and active
        (RN01), so their slots are only public while they can be booked.
        """
        instructor = find_bookable_instructor(self._db, instructor_ref)
        if instructor is None:
            msg = "Instructor not found or not accepting bookings"
            raise LookupError(msg)
        now = datetime.now(UTC)
        return [slot for slot in self.list_slots(instructor.user_id) if slot.starts_at > now]

    def delete_slot(self, instructor_id: str, slot_id: str) -> None:
        """Remove one of the instructor's slots.

        A slot that a (cancelled) booking still refers to is kept as history and marked
        BLOQUEADO, so it disappears from the agenda without breaking that booking; any other
        slot is deleted.

        Raises ``ValueError`` if the slot is not found for the instructor or is reserved.
        """
        slot = self._db.exec(
            select(Slot).where(col(Slot.id) == slot_id, col(Slot.instructor_id) == instructor_id)
        ).first()
        if not slot or slot.status == SlotStatus.BLOQUEADO.value:
            msg = f"Slot {slot_id} not found for instructor {instructor_id}"
            raise ValueError(msg)
        if slot.status == SlotStatus.RESERVADO.value:
            msg = f"Cannot delete reserved slot {slot_id}"
            raise ValueError(msg)
        has_history = self._db.exec(
            select(BookingSlot.id).where(col(BookingSlot.slot_id) == slot_id)
        ).first()
        if has_history:
            slot.status = SlotStatus.BLOQUEADO.value
        else:
            self._db.delete(slot)
        self._db.flush()

    def get_slots_by_ids(self, slot_ids: list[str]) -> list[Slot]:
        """Return the slots matching the given IDs."""
        return list(self._db.exec(select(Slot).where(col(Slot.id).in_(slot_ids))).all())
