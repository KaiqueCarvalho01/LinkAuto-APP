"""Scheduled booking automations: pending timeouts, auto-completion and lesson reminders."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Protocol

from app.domain.booking import BookingStatus

logger = logging.getLogger("app.services.booking_scheduler")


class BookingAutomationPort(Protocol):
    """Persistence operations required by ``BookingScheduler``."""

    def list_pending_expired(self, cutoff_utc: datetime) -> list[str]:
        """Return IDs of PENDENTE bookings created at or before ``cutoff_utc``."""
        ...

    def list_confirmed_ready(self, cutoff_utc: datetime) -> list[str]:
        """Return IDs of CONFIRMADA bookings whose last slot ended by ``cutoff_utc``."""
        ...

    def list_unreminded_upcoming(self, start_cutoff: datetime, end_cutoff: datetime) -> list[str]:
        """Return IDs of unreminded CONFIRMADA bookings starting between the cutoffs."""
        ...

    def mark_reminder_sent(self, booking_id: str) -> None:
        """Record that the lesson reminder for the booking was sent."""
        ...

    def transition_to(self, booking_id: str, status: BookingStatus, reason: str) -> None:
        """Move the booking to ``status``, recording ``reason``."""
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

        Per-booking failures are logged and reported in the result instead of raised.
        """
        reference = self._now_utc(now_utc)
        cutoff = reference - timedelta(hours=24)
        pending_ids = self._automation_port.list_pending_expired(cutoff)

        success_ids = []
        failed_ids = []

        for booking_id in pending_ids:
            try:
                self._automation_port.transition_to(
                    booking_id, BookingStatus.CANCELADA, "AUTO_TIMEOUT_24H"
                )
                success_ids.append(booking_id)
            except Exception as exc:
                logger.warning(
                    "Scheduler failed to cancel expired booking %s",
                    booking_id,
                    extra={
                        "event": "scheduler.pending_timeout.failure",
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

    def run_confirmed_completion(self, now_utc: datetime | None = None) -> BookingSchedulerResult:
        """Mark CONFIRMADA bookings as REALIZADA 2 hours after their last slot ends.

        Per-booking failures are logged and reported in the result instead of raised.
        """
        reference = self._now_utc(now_utc)
        cutoff = reference - timedelta(hours=2)
        ready_ids = self._automation_port.list_confirmed_ready(cutoff)

        success_ids = []
        failed_ids = []

        for booking_id in ready_ids:
            try:
                self._automation_port.transition_to(
                    booking_id, BookingStatus.REALIZADA, "AUTO_COMPLETE_PLUS_2H"
                )
                success_ids.append(booking_id)
            except Exception as exc:
                logger.warning(
                    "Scheduler failed to complete finished booking %s",
                    booking_id,
                    extra={
                        "event": "scheduler.confirmed_completion.failure",
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

    def run_lesson_reminders(self, now_utc: datetime | None = None) -> BookingSchedulerResult:
        """Email reminders for confirmed lessons starting in 23-25 hours and mark them reminded.

        The reminder goes to the student and instructor when a reminder sender is set.
        Per-booking failures are logged and reported in the result instead of raised.
        """
        reference = self._now_utc(now_utc)
        start_cutoff = reference + timedelta(hours=23)
        end_cutoff = reference + timedelta(hours=25)

        upcoming_ids = self._automation_port.list_unreminded_upcoming(start_cutoff, end_cutoff)

        success_ids = []
        failed_ids = []

        for booking_id in upcoming_ids:
            try:
                if self._reminder_sender:
                    self._reminder_sender.send_lesson_reminder(booking_id)

                # Mark as reminded
                self._automation_port.mark_reminder_sent(booking_id)
                success_ids.append(booking_id)
            except Exception as exc:
                logger.warning(
                    "Scheduler failed to send lesson reminder for booking %s",
                    booking_id,
                    extra={
                        "event": "scheduler.lesson_reminder.failure",
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
