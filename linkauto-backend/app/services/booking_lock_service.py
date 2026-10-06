"""Atomic, all-or-nothing reservation of booking slots."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import TYPE_CHECKING, Any, Protocol, cast

from sqlalchemy import bindparam, text

from app.domain.booking import MIN_SLOTS_PER_BOOKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy import CursorResult
    from sqlalchemy.orm import Session


class SlotReservationConflictError(RuntimeError):
    """Raised when any requested slot is no longer available for reservation."""


class SlotReservationStore(Protocol):
    """Storage able to reserve a set of slots atomically."""

    def reserve_if_all_available(self, slot_ids: Sequence[str]) -> bool:
        """Reserve all given slots and return ``True``, or reserve none and return ``False``."""
        ...


@dataclass
class InMemorySlotReservationStore:
    """Lock-protected in-memory slot reservation store keyed by slot ID."""

    _status: dict[str, str] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def seed_slots(self, slot_ids: Sequence[str], available_status: str = "DISPONIVEL") -> None:
        """Set the status of the given slots (``DISPONIVEL`` by default)."""
        with self._lock:
            for slot_id in slot_ids:
                self._status[slot_id] = available_status

    def reserve_if_all_available(self, slot_ids: Sequence[str]) -> bool:
        """Reserve the slots if all are ``DISPONIVEL``; return whether they were reserved."""
        slot_ids = list(dict.fromkeys(slot_ids))
        with self._lock:
            if any(self._status.get(slot_id) != "DISPONIVEL" for slot_id in slot_ids):
                return False
            for slot_id in slot_ids:
                self._status[slot_id] = "RESERVADO"
            return True


class SqlAlchemySlotReservationStore:
    """Slot reservation store backed by a conditional ``UPDATE`` on the ``slots`` table."""

    _TABLE_NAME: str = "slots"
    _RESERVE_STATEMENT = text(
        """
        UPDATE slots
        SET status = :reserved_status
        WHERE id IN :slot_ids
          AND status = :available_status
        """
    ).bindparams(bindparam("slot_ids", expanding=True))

    def __init__(
        self,
        session: Session,
        *,
        available_status: str = "DISPONIVEL",
        reserved_status: str = "RESERVADO",
    ) -> None:
        """Store the session and the slot status values meaning available/reserved."""
        self._session = session
        self._available_status = available_status
        self._reserved_status = reserved_status

    def reserve_if_all_available(self, slot_ids: Sequence[str]) -> bool:
        """Reserve the slots in one transaction if all are available; return the outcome.

        Rolls back and returns ``False`` unless every slot was updated; ``False`` for no IDs.
        """
        unique_slot_ids = list(dict.fromkeys(slot_ids))
        if not unique_slot_ids:
            return False

        transaction = self._session.begin()
        try:
            # A text() UPDATE always yields a CursorResult, which carries rowcount
            result = cast(
                "CursorResult[Any]",
                self._session.execute(
                    self._RESERVE_STATEMENT,
                    {
                        "reserved_status": self._reserved_status,
                        "available_status": self._available_status,
                        "slot_ids": unique_slot_ids,
                    },
                ),
            )
        except Exception:
            transaction.rollback()
            raise
        if result.rowcount != len(unique_slot_ids):
            transaction.rollback()
            return False
        transaction.commit()
        return True


class BookingLockService:
    """Reserve booking slots all-or-nothing, enforcing RN02's minimum slot count."""

    def __init__(self, store: SlotReservationStore) -> None:
        """Store the slot reservation backend."""
        self._store = store

    def reserve_slots(self, slot_ids: Sequence[str]) -> None:
        """Reserve the given slots, ignoring duplicate IDs.

        Raises ``ValueError`` if fewer than two unique slots are given (RN02) and
        ``SlotReservationConflictError`` if any slot is no longer available.
        """
        unique_slot_ids = list(dict.fromkeys(slot_ids))
        if len(unique_slot_ids) < MIN_SLOTS_PER_BOOKING:
            msg = "Booking requires at least two unique slots."
            raise ValueError(msg)

        if not self._store.reserve_if_all_available(unique_slot_ids):
            msg = "One or more requested slots are no longer available."
            raise SlotReservationConflictError(msg)
