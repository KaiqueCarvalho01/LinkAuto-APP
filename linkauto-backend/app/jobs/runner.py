"""The scheduled jobs, shared by the CLI (``python -m app.jobs``) and the admin endpoints."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from app.services.booking_automation_store import SqlAlchemyBookingAutomationPort
from app.services.booking_notifier import BookingNotifier
from app.services.booking_scheduler import BookingScheduler, BookingSchedulerResult

if TYPE_CHECKING:
    from sqlmodel import Session

    from app.services.notification_service import NotificationService


class Job(StrEnum):
    """Jobs that can be run on a schedule."""

    TIMEOUT = "timeout"
    COMPLETION = "completion"
    REMINDER = "reminder"


def run_job(
    job: Job, db: Session, notification_service: NotificationService | None
) -> BookingSchedulerResult:
    """Run one job in the session. The caller commits."""
    port = SqlAlchemyBookingAutomationPort(db, notification_service)
    scheduler = BookingScheduler(port, reminder_sender=BookingNotifier(db, notification_service))
    match job:
        case Job.TIMEOUT:
            return scheduler.run_pending_timeout()
        case Job.COMPLETION:
            return scheduler.run_confirmed_completion()
        case Job.REMINDER:
            return scheduler.run_lesson_reminders()
