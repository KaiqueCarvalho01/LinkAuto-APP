from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

from app.domain.booking import BookingStatus


class BookingAutomationPort(Protocol):
    def list_pending_expired(self, cutoff_utc: datetime) -> list[str]:
        ...

    def list_confirmed_ready(self, cutoff_utc: datetime) -> list[str]:
        ...

    def transition_to(self, booking_id: str, status: BookingStatus, reason: str) -> None:
        ...


@dataclass(slots=True)
class BookingSchedulerResult:
    processed: int
    booking_ids: list[str]


class BookingScheduler:
    def __init__(self, automation_port: BookingAutomationPort) -> None:
        self._automation_port = automation_port

    @staticmethod
    def _now_utc(now_utc: datetime | None = None) -> datetime:
        if now_utc is None:
            return datetime.now(timezone.utc)
        if now_utc.tzinfo is None:
            return now_utc.replace(tzinfo=timezone.utc)
        return now_utc.astimezone(timezone.utc)

    def run_pending_timeout(self, now_utc: datetime | None = None) -> BookingSchedulerResult:
        reference = self._now_utc(now_utc)
        cutoff = reference - timedelta(hours=24)
        pending_ids = self._automation_port.list_pending_expired(cutoff)
        for booking_id in pending_ids:
            self._automation_port.transition_to(
                booking_id, BookingStatus.CANCELADA, "AUTO_TIMEOUT_24H"
            )
        return BookingSchedulerResult(processed=len(pending_ids), booking_ids=pending_ids)

    def run_confirmed_completion(self, now_utc: datetime | None = None) -> BookingSchedulerResult:
        reference = self._now_utc(now_utc)
        cutoff = reference - timedelta(hours=2)
        ready_ids = self._automation_port.list_confirmed_ready(cutoff)
        for booking_id in ready_ids:
            self._automation_port.transition_to(
                booking_id, BookingStatus.REALIZADA, "AUTO_COMPLETE_PLUS_2H"
            )
        return BookingSchedulerResult(processed=len(ready_ids), booking_ids=ready_ids)
