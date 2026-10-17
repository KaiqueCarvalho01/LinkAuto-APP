"""Scheduled booking automations: pending timeouts, auto-completion and lesson reminders.

The jobs are safe to run more than once, also concurrently: each booking is claimed with a
conditional update, so a booking handled by one run is skipped by the other.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger("app.services.booking_scheduler")

PENDING_TIMEOUT = timedelta(hours=24)
COMPLETION_DELAY = timedelta(hours=2)
REMINDER_WINDOW = (timedelta(hours=23), timedelta(hours=25))
TIMEOUT_REASON = "AUTO_TIMEOUT_24H"


class BookingAutomationPort(Protocol):
    """Persistence operations required by ``BookingScheduler``.

    The ``cancel_expired``, ``complete`` and ``claim_reminder`` methods return ``False`` when
    the booking no longer qualifies (for example, another run already handled it).
    """

    def list_pending_expired(self, cutoff_utc: datetime) -> list[str]:
        """Return IDs of PENDENTE bookings created at or before ``cutoff_utc``."""
        ...

    def list_confirmed_ready(self, cutoff_utc: datetime) -> list[str]:
        """Return IDs of CONFIRMADA bookings whose last slot ended by ``cutoff_utc``."""
        ...

    def list_unreminded_upcoming(self, start_cutoff: datetime, end_cutoff: datetime) -> list[str]:
        """Return IDs of unreminded CONFIRMADA bookings starting between the cutoffs."""
        ...

    def cancel_expired(self, booking_id: str, reason: str) -> bool:
        """Cancel the still-PENDENTE booking as SISTEMA, releasing its slots."""
        ...

    def complete(self, booking_id: str) -> bool:
        """Move the still-CONFIRMADA booking to REALIZADA."""
        ...

    def claim_reminder(self, booking_id: str) -> bool:
        """Flag the CONFIRMADA booking's reminder as sent, if it was not flagged yet."""
        ...


class LessonReminderSender(Protocol):
    """Sends the 24h lesson reminder of a booking (e.g. ``BookingNotifier``)."""

    def send_lesson_reminder(self, booking_id: str) -> None:
        """Remind the booking's participants of the lesson."""
        ...


@dataclass(slots=True)
class BookingSchedulerResult:
    """Summary of a scheduler run: succeeded and failed booking IDs."""

    processed: int
    booking_ids: list[str]
    failed: int = 0
    failed_booking_ids: list[str] = field(default_factory=list)


class BookingScheduler:
    """Run periodic booking automations: timeouts, completions and lesson reminders."""

    def __init__(
        self,
        automation_port: BookingAutomationPort,
        reminder_sender: LessonReminderSender | None = None,
    ) -> None:
        """Store the automation port and the optional reminder sender."""
        self._automation_port = automation_port
        self._reminder_sender = reminder_sender

    @staticmethod
    def _now_utc(now_utc: datetime | None = None) -> datetime:
        if now_utc is None:
            return datetime.now(UTC)
        if now_utc.tzinfo is None:
            return now_utc.replace(tzinfo=UTC)
        return now_utc.astimezone(UTC)

    def run_pending_timeout(self, now_utc: datetime | None = None) -> BookingSchedulerResult:
        """Cancel PENDENTE bookings created more than 24 hours ago (reason ``AUTO_TIMEOUT_24H``).

        Their slots are released and both participants are notified. Per-booking failures
        are logged and reported in the result instead of raised.
        """
        cutoff = self._now_utc(now_utc) - PENDING_TIMEOUT
        return self._run(
            "pending_timeout",
            self._automation_port.list_pending_expired(cutoff),
            lambda booking_id: self._automation_port.cancel_expired(booking_id, TIMEOUT_REASON),
        )

    def run_confirmed_completion(self, now_utc: datetime | None = None) -> BookingSchedulerResult:
        """Mark CONFIRMADA bookings as REALIZADA 2 hours after their last slot ends.

        Per-booking failures are logged and reported in the result instead of raised.
        """
        cutoff = self._now_utc(now_utc) - COMPLETION_DELAY
        return self._run(
            "confirmed_completion",
            self._automation_port.list_confirmed_ready(cutoff),
            self._automation_port.complete,
        )

    def run_lesson_reminders(self, now_utc: datetime | None = None) -> BookingSchedulerResult:
        """Remind participants of confirmed lessons starting in 23-25 hours, once per booking.

        The reminder is flagged as sent before it is e-mailed, so overlapping runs send it at
        most once. Per-booking failures are logged and reported in the result instead of raised.
        """
        reference = self._now_utc(now_utc)
        start, end = (reference + offset for offset in REMINDER_WINDOW)

        def remind(booking_id: str) -> bool:
            if not self._automation_port.claim_reminder(booking_id):
                return False
            if self._reminder_sender:
                self._reminder_sender.send_lesson_reminder(booking_id)
            return True

        return self._run(
            "lesson_reminder",
            self._automation_port.list_unreminded_upcoming(start, end),
            remind,
        )

    @staticmethod
    def _run(
        job: str, booking_ids: list[str], handle: Callable[[str], bool]
    ) -> BookingSchedulerResult:
        success_ids: list[str] = []
        failed_ids: list[str] = []
        for booking_id in booking_ids:
            try:
                if handle(booking_id):
                    success_ids.append(booking_id)
            except Exception as exc:
                logger.warning(
                    "Scheduler job %s failed for booking %s",
                    job,
                    booking_id,
                    extra={
                        "event": f"scheduler.{job}.failure",
                        "booking_id": booking_id,
                        "error": str(exc),
                    },
                    exc_info=True,
                )
                failed_ids.append(booking_id)
        return BookingSchedulerResult(
            processed=len(success_ids),
            booking_ids=success_ids,
            failed=len(failed_ids),
            failed_booking_ids=failed_ids,
        )
