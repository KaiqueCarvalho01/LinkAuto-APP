from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from threading import Lock
from typing import Protocol

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session


class SlotReservationConflictError(RuntimeError):
    pass


class SlotReservationStore(Protocol):
    def reserve_if_all_available(self, slot_ids: Sequence[str]) -> bool:
        ...


@dataclass
class InMemorySlotReservationStore:
    _status: dict[str, str] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def seed_slots(self, slot_ids: Sequence[str], available_status: str = "DISPONIVEL") -> None:
        with self._lock:
            for slot_id in slot_ids:
                self._status[slot_id] = available_status

    def reserve_if_all_available(self, slot_ids: Sequence[str]) -> bool:
        slot_ids = list(dict.fromkeys(slot_ids))
        with self._lock:
            if any(self._status.get(slot_id) != "DISPONIVEL" for slot_id in slot_ids):
                return False
            for slot_id in slot_ids:
                self._status[slot_id] = "RESERVADO"
            return True


class SqlAlchemySlotReservationStore:
    def __init__(
        self,
        session: Session,
        *,
        table_name: str = "slots",
        available_status: str = "DISPONIVEL",
        reserved_status: str = "RESERVADO",
    ) -> None:
        self._session = session
        self._table_name = table_name
        self._available_status = available_status
        self._reserved_status = reserved_status

    def reserve_if_all_available(self, slot_ids: Sequence[str]) -> bool:
        unique_slot_ids = list(dict.fromkeys(slot_ids))
        if not unique_slot_ids:
            return False

        transaction = self._session.begin()
        try:
            statement = text(
                f"""
                UPDATE {self._table_name}
                SET status = :reserved_status
                WHERE id IN :slot_ids
                  AND status = :available_status
                """
            ).bindparams(bindparam("slot_ids", expanding=True))

            result = self._session.execute(
                statement,
                {
                    "reserved_status": self._reserved_status,
                    "available_status": self._available_status,
                    "slot_ids": unique_slot_ids,
                },
            )
            success = result.rowcount == len(unique_slot_ids)
            if success:
                transaction.commit()
                return True
            transaction.rollback()
            return False
        except Exception:
            transaction.rollback()
            raise


class BookingLockService:
    def __init__(self, store: SlotReservationStore) -> None:
        self._store = store

    def reserve_slots(self, slot_ids: Sequence[str]) -> None:
        unique_slot_ids = list(dict.fromkeys(slot_ids))
        if len(unique_slot_ids) < 2:
            raise ValueError("Booking requires at least two unique slots.")

        if not self._store.reserve_if_all_available(unique_slot_ids):
            raise SlotReservationConflictError(
                "One or more requested slots are no longer available."
            )
