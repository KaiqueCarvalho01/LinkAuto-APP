"""E-mails about a booking, addressed by name, with the lesson time and a link to the app."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlmodel import col, select

from app.core import get_settings
from app.models.booking import Booking, BookingSlot, CancelledBy
from app.models.slot import Slot
from app.models.user import InstructorProfile, StudentProfile, User
from app.services.notification_templates import (
    CANCELLED_BY_LABELS,
    NO_COMMENT,
    NO_REASON,
    EmailTemplateName,
    render_email,
)

if TYPE_CHECKING:
    from datetime import datetime

    from sqlmodel import Session

    from app.core import Settings
    from app.services.notification_service import NotificationService

STUDENT_FALLBACK_NAME = "Aluno"
INSTRUCTOR_FALLBACK_NAME = "Instrutor"
# Where each side manages its bookings in the web app
STUDENT_BOOKINGS_PATH = "/my-lessons"
INSTRUCTOR_BOOKINGS_PATH = "/instructor/dashboard"

_WEEKDAYS = (
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
)


def format_lesson_time(starts_at: datetime, ends_at: datetime) -> str:
    """Return e.g. ``sábado, 18/10/2026, das 09:00 às 11:00``.

    Uses the stored (UTC) wall-clock time, the same way the web app shows slot times.
    """
    return (
        f"{_WEEKDAYS[starts_at.weekday()]}, {starts_at:%d/%m/%Y}, "
        f"das {starts_at:%H:%M} às {ends_at:%H:%M}"
    )


@dataclass(frozen=True, slots=True)
class _Party:
    email: str | None
    name: str
    link: str


class BookingNotifier:
    """Send the booking e-mails, one per recipient. Without a notification service, no-op."""

    def __init__(
        self,
        db: Session,
        notification_service: NotificationService | None,
        settings: Settings | None = None,
    ) -> None:
        """Store the session, the optional notification service and the settings."""
        self._db = db
        self._notification_service = notification_service
        self._settings = settings or get_settings()

    def booking_requested(self, booking: Booking) -> None:
        """Tell the instructor a student asked for a lesson."""
        student, instructor = self._parties(booking)
        lesson_time = self._lesson_time(booking)
        self._send(
            EmailTemplateName.BOOKING_REQUESTED,
            instructor,
            lesson_time,
            student_name=student.name,
        )

    def booking_confirmed(self, booking: Booking) -> None:
        """Tell the student the instructor confirmed the lesson."""
        student, instructor = self._parties(booking)
        lesson_time = self._lesson_time(booking)
        self._send(
            EmailTemplateName.BOOKING_CONFIRMED,
            student,
            lesson_time,
            instructor_name=instructor.name,
        )

    def booking_cancelled(self, booking: Booking) -> None:
        """Tell the other party (both, for system or admin cancellations) of a cancellation."""
        student, instructor = self._parties(booking)
        lesson_time = self._lesson_time(booking)
        cancelled_by = booking.cancelled_by or CancelledBy.SISTEMA.value
        label = CANCELLED_BY_LABELS.get(cancelled_by, "").format(
            student_name=student.name, instructor_name=instructor.name
        )
        if cancelled_by == CancelledBy.ALUNO.value:
            recipients = [(instructor, student)]
        elif cancelled_by == CancelledBy.INSTRUTOR.value:
            recipients = [(student, instructor)]
        else:
            recipients = [(student, instructor), (instructor, student)]
        for recipient, other in recipients:
            self._send(
                EmailTemplateName.BOOKING_CANCELLED,
                recipient,
                lesson_time,
                other_name=other.name,
                cancelled_by=label,
                reason=booking.cancellation_reason or NO_REASON,
            )

    def lesson_reminder(self, booking: Booking) -> None:
        """Remind the student and the instructor of the lesson."""
        student, instructor = self._parties(booking)
        lesson_time = self._lesson_time(booking)
        for recipient, other in ((student, instructor), (instructor, student)):
            self._send(
                EmailTemplateName.LESSON_REMINDER, recipient, lesson_time, other_name=other.name
            )

    def send_lesson_reminder(self, booking_id: str) -> None:
        """Remind the participants of the booking with this ID (``LessonReminderSender``)."""
        booking = self._db.get(Booking, booking_id)
        if booking is not None:
            self.lesson_reminder(booking)

    def message_received(self, booking: Booking, *, sender_id: str, content: str) -> None:
        """Forward a booking chat message to the participant who did not send it."""
        student, instructor = self._parties(booking)
        lesson_time = self._lesson_time(booking)
        sender, recipient = (
            (student, instructor) if sender_id == booking.student_id else (instructor, student)
        )
        self._send(
            EmailTemplateName.BOOKING_MESSAGE,
            recipient,
            lesson_time,
            sender_name=sender.name,
            content=content,
        )

    def review_received(
        self, booking: Booking, *, reviewer_id: str, rating: int, comment: str | None
    ) -> None:
        """Tell the reviewed participant about their new review."""
        student, instructor = self._parties(booking)
        lesson_time = self._lesson_time(booking)
        reviewer, recipient = (
            (student, instructor) if reviewer_id == booking.student_id else (instructor, student)
        )
        self._send(
            EmailTemplateName.REVIEW_RECEIVED,
            recipient,
            lesson_time,
            reviewer_name=reviewer.name,
            rating=str(rating),
            comment=comment or NO_COMMENT,
        )

    def _send(
        self, template: EmailTemplateName, recipient: _Party, lesson_time: str, **values: str
    ) -> None:
        if self._notification_service is None or not recipient.email:
            return
        self._notification_service.dispatch(
            render_email(
                template,
                [recipient.email],
                recipient_name=recipient.name,
                link=recipient.link,
                lesson_time=lesson_time,
                **values,
            )
        )

    def _parties(self, booking: Booking) -> tuple[_Party, _Party]:
        student_user = self._db.get(User, booking.student_id)
        instructor_user = self._db.get(User, booking.instructor_id)
        student_profile = self._db.get(StudentProfile, booking.student_id)
        instructor_profile = self._db.get(InstructorProfile, booking.instructor_id)
        student = _Party(
            email=student_user.email if student_user else None,
            name=(student_profile.full_name if student_profile else None) or STUDENT_FALLBACK_NAME,
            link=self._settings.frontend_link(STUDENT_BOOKINGS_PATH),
        )
        instructor = _Party(
            email=instructor_user.email if instructor_user else None,
            name=(instructor_profile.full_name if instructor_profile else None)
            or INSTRUCTOR_FALLBACK_NAME,
            link=self._settings.frontend_link(INSTRUCTOR_BOOKINGS_PATH),
        )
        return student, instructor

    def _lesson_time(self, booking: Booking) -> str:
        slots = self._db.exec(
            select(Slot)
            .join(BookingSlot, col(BookingSlot.slot_id) == col(Slot.id))
            .where(col(BookingSlot.booking_id) == booking.id)
            .order_by(col(Slot.starts_at))
        ).all()
        if not slots:
            return "data a combinar"
        return format_lesson_time(slots[0].starts_at, slots[-1].ends_at)
