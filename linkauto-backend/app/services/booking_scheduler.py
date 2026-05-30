from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

from app.domain.booking import BookingStatus
from app.services.notification_service import NotificationService, NotificationPayload, NotificationEvent


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

    def run_lesson_reminders(self, now_utc: datetime | None = None) -> BookingSchedulerResult:
        reference = self._now_utc(now_utc)
        start_cutoff = reference + timedelta(hours=23)
        end_cutoff = reference + timedelta(hours=25)
        
        upcoming_ids = self._automation_port.list_unreminded_upcoming(start_cutoff, end_cutoff)
        
        for booking_id in upcoming_ids:
            # Trigger email reminder
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

        return BookingSchedulerResult(processed=len(upcoming_ids), booking_ids=upcoming_ids)
