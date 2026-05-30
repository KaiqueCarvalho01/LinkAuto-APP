from __future__ import annotations

from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.slot import Slot, SlotStatus


class SlotOverlapError(ValueError):
    pass


class SlotService:
    def __init__(self, db: Session):
        self._db = db

    def create_slot(
        self,
        instructor_id: str,
        starts_at: datetime,
        ends_at: datetime,
    ) -> Slot:
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
            raise SlotOverlapError(
                f"Slot overlaps with existing slot {overlap.id} "
                f"({overlap.starts_at} - {overlap.ends_at})"
            )

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
        query = self._db.query(Slot).filter(Slot.instructor_id == instructor_id)
        if status:
            query = query.filter(Slot.status == status.value)
        return query.order_by(Slot.starts_at).all()

    def delete_slot(self, instructor_id: str, slot_id: str) -> None:
        slot = (
            self._db.query(Slot)
            .filter(Slot.id == slot_id, Slot.instructor_id == instructor_id)
            .first()
        )
        if not slot:
            raise ValueError(f"Slot {slot_id} not found for instructor {instructor_id}")
        if slot.status == SlotStatus.RESERVADO.value:
            raise ValueError(f"Cannot delete reserved slot {slot_id}")
        self._db.delete(slot)
        self._db.flush()

    def get_slots_by_ids(self, slot_ids: list[str]) -> list[Slot]:
        return self._db.query(Slot).filter(Slot.id.in_(slot_ids)).all()
