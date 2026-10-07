"""Management of instructors' availability slots."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import and_

from app.models.slot import Slot, SlotStatus
from app.models.user import InstructorProfile

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.orm import Session


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
        """Create a DISPONIVEL slot, raising ``SlotOverlapError`` if it overlaps an existing one."""
        overlap = (
            self._db.query(Slot)
            .filter(
                and_(
                    Slot.instructor_id == instructor_id,
                    Slot.starts_at < ends_at,
                    Slot.ends_at > starts_at,
                )
            )
            .first()
        )
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

        ``instructor_id`` may be either the instructor's user ID or profile slug.
        """
        prof = (
            self._db.query(InstructorProfile)
            .filter(InstructorProfile.slug == instructor_id)
            .first()
        )
        effective_id = prof.user_id if prof else instructor_id

        query = self._db.query(Slot).filter(Slot.instructor_id == effective_id)
        if status:
            query = query.filter(Slot.status == status.value)
        return query.order_by(Slot.starts_at).all()

    def delete_slot(self, instructor_id: str, slot_id: str) -> None:
        """Delete an instructor's slot.

        Raises ``ValueError`` if the slot is not found for the instructor or is reserved.
        """
        slot = (
            self._db.query(Slot)
            .filter(Slot.id == slot_id, Slot.instructor_id == instructor_id)
            .first()
        )
        if not slot:
            msg = f"Slot {slot_id} not found for instructor {instructor_id}"
            raise ValueError(msg)
        if slot.status == SlotStatus.RESERVADO.value:
            msg = f"Cannot delete reserved slot {slot_id}"
            raise ValueError(msg)
        self._db.delete(slot)
        self._db.flush()

    def get_slots_by_ids(self, slot_ids: list[str]) -> list[Slot]:
        """Return the slots matching the given IDs."""
        return self._db.query(Slot).filter(Slot.id.in_(slot_ids)).all()
