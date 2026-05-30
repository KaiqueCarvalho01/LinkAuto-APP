from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import logging
from typing import Protocol

from app.domain.booking import BookingStatus
from app.services.notification_service import NotificationService, NotificationPayload, NotificationEvent

logger = logging.getLogger("app.services.booking_scheduler")


class BookingAutomationPort(Protocol):
    def list_pending_expired(self, cutoff_utc: datetime) -> list[str]:
        ...

    def list_confirmed_ready(self, cutoff_utc: datetime) -> list[str]:
        ...

    def list_unreminded_upcoming(self, start_cutoff: datetime, end_cutoff: datetime) -> list[str]:
        ...

    def mark_reminder_sent(self, booking_id: str) -> None:
        ...

    def transition_to(self, booking_id: str, status: BookingStatus, reason: str) -> None:
        ...

    def get_booking_emails(self, booking_id: str) -> tuple[str | None, str | None]:
        ...


@dataclass(slots=True)
class BookingSchedulerResult:
    processed: int
    booking_ids: list[str]
    failed: int = 0
    failed_booking_ids: list[str] = field(default_factory=list)


class BookingScheduler:
    def __init__(
        self,
        automation_port: BookingAutomationPort,
        notification_service: NotificationService | None = None,
    ) -> None:
        self._automation_port = automation_port
        self._notification_service = notification_service

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
                    f"Scheduler failed to cancel expired booking {booking_id}: {str(exc)}",
                    extra={
                        "event": "scheduler.pending_timeout.failure",
                        "booking_id": booking_id,
                        "error": str(exc)
                    }
                )
                failed_ids.append(booking_id)
                
        return BookingSchedulerResult(
            processed=len(success_ids),
            booking_ids=success_ids,
            failed=len(failed_ids),
            failed_booking_ids=failed_ids
        )

    def run_confirmed_completion(self, now_utc: datetime | None = None) -> BookingSchedulerResult:
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
                    f"Scheduler failed to complete finished booking {booking_id}: {str(exc)}",
                    extra={
                        "event": "scheduler.confirmed_completion.failure",
                        "booking_id": booking_id,
                        "error": str(exc)
                    }
                )
                failed_ids.append(booking_id)
                
        return BookingSchedulerResult(
            processed=len(success_ids),
            booking_ids=success_ids,
            failed=len(failed_ids),
            failed_booking_ids=failed_ids
        )

    def run_lesson_reminders(self, now_utc: datetime | None = None) -> BookingSchedulerResult:
        reference = self._now_utc(now_utc)
        start_cutoff = reference + timedelta(hours=23)
        end_cutoff = reference + timedelta(hours=25)
        
        upcoming_ids = self._automation_port.list_unreminded_upcoming(start_cutoff, end_cutoff)
        
        success_ids = []
        failed_ids = []
        
        for booking_id in upcoming_ids:
            try:
                # Trigger e-mail reminder
                student_email, instructor_email = self._automation_port.get_booking_emails(booking_id)
                recipients = []
                if student_email:
                    recipients.append(student_email)
                if instructor_email:
                    recipients.append(instructor_email)

                if recipients and self._notification_service:
                    self._notification_service.dispatch(
                        NotificationPayload(
                            event=NotificationEvent.LESSON_REMINDER_24H,
                            subject="Lembrete de aula LinkAuto",
                            body=f"Lembrete: Sua aula LinkAuto (Agendamento: {booking_id}) iniciará em aproximadamente 24 horas.",
                            recipients=recipients,
                        )
                    )

                # Mark as reminded
                self._automation_port.mark_reminder_sent(booking_id)
                success_ids.append(booking_id)
            except Exception as exc:
                logger.warning(
                    f"Scheduler failed to send lesson reminder for booking {booking_id}: {str(exc)}",
                    extra={
                        "event": "scheduler.lesson_reminder.failure",
                        "booking_id": booking_id,
                        "error": str(exc)
                    }
                )
                failed_ids.append(booking_id)

        return BookingSchedulerResult(
            processed=len(success_ids),
            booking_ids=success_ids,
            failed=len(failed_ids),
            failed_booking_ids=failed_ids
        )
