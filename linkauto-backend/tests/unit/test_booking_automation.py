from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, override

from app.domain.booking import BookingStatus
from app.models.booking import Booking, BookingSlot
from app.models.slot import Slot, SlotStatus
from app.models.user import (
    DetranStatus,
    InstructorProfile,
    StudentProfile,
    User,
    UserRole,
)
from app.services.booking_automation_store import SqlAlchemyBookingAutomationPort
from app.services.booking_notifier import BookingNotifier
from app.services.booking_scheduler import BookingAutomationPort, BookingScheduler
from app.services.notification_service import InMemoryEmailGateway, NotificationService

if TYPE_CHECKING:
    from sqlmodel import Session


def _seed_full_booking(
    db_session: Session, status: str, starts_offset_hours: int, booking_id: str = "book-auto"
) -> Booking:
    inst = User(
        id="auto-inst", email="autoinst@t.com", password_hash="h", roles=[UserRole.INSTRUTOR.value]
    )
    inst_p = InstructorProfile(
        user_id="auto-inst",
        full_name="I",
        phone="1",
        city="C",
        state="SP",
        detran_status=DetranStatus.APROVADO,
    )
    stu = User(
        id="auto-stu", email="autostu@t.com", password_hash="h", roles=[UserRole.ALUNO.value]
    )
    stu_p = StudentProfile(user_id="auto-stu", full_name="S", phone="2", city="C", state="SP")

    now = datetime.now(UTC)
    base = now + timedelta(hours=starts_offset_hours)
    slot1 = Slot(
        instructor_id="auto-inst",
        starts_at=base,
        ends_at=base + timedelta(hours=1),
        status=SlotStatus.RESERVADO.value,
    )
    slot2 = Slot(
        instructor_id="auto-inst",
        starts_at=base + timedelta(hours=1),
        ends_at=base + timedelta(hours=2),
        status=SlotStatus.RESERVADO.value,
    )

    # Set created_at to 48 hours ago for pending timeout testing
    booking = Booking(
        id=booking_id,
        student_id="auto-stu",
        instructor_id="auto-inst",
        status=status,
        created_at=now - timedelta(hours=48),
    )
    db_session.add_all([inst, stu])
    db_session.flush()
    db_session.add_all([inst_p, stu_p])
    db_session.flush()
    db_session.add_all([slot1, slot2, booking])
    db_session.flush()

    db_session.add_all(
        [
            BookingSlot(booking_id=booking.id, slot_id=slot1.id),
            BookingSlot(booking_id=booking.id, slot_id=slot2.id),
        ]
    )
    db_session.flush()
    return booking


class TestBookingAutomationPort:
    def test_pending_timeout_cancels_old_bookings(self, db_session: Session) -> None:
        booking = _seed_full_booking(
            db_session, BookingStatus.PENDENTE.value, starts_offset_hours=-48
        )
        port = SqlAlchemyBookingAutomationPort(db_session)
        scheduler = BookingScheduler(port)

        result = scheduler.run_pending_timeout()

        db_session.refresh(booking)
        assert booking.status == BookingStatus.CANCELADA.value
        assert result.processed == 1

    def test_confirmed_completion_after_2h(self, db_session: Session) -> None:
        booking = _seed_full_booking(
            db_session, BookingStatus.CONFIRMADA.value, starts_offset_hours=-6
        )
        port = SqlAlchemyBookingAutomationPort(db_session)
        scheduler = BookingScheduler(port)

        result = scheduler.run_confirmed_completion()

        db_session.refresh(booking)
        assert booking.status == BookingStatus.REALIZADA.value
        assert result.processed == 1

    def test_lesson_reminder_cron_triggers(self, db_session: Session) -> None:

        gateway = InMemoryEmailGateway()
        notification_svc = NotificationService(email_gateway=gateway)

        booking = _seed_full_booking(
            db_session,
            BookingStatus.CONFIRMADA.value,
            starts_offset_hours=24,
            booking_id="book-reminder",
        )

        port = SqlAlchemyBookingAutomationPort(db_session)
        scheduler = BookingScheduler(
            port, reminder_sender=BookingNotifier(db_session, notification_svc)
        )

        result = scheduler.run_lesson_reminders()

        db_session.refresh(booking)
        assert booking.reminder_sent is True
        assert result.processed == 1

        # One reminder each for the student and the instructor
        assert [m["recipients"] for m in gateway.sent_messages] == [
            ["autostu@t.com"],
            ["autoinst@t.com"],
        ]
        assert all("Lembrete" in m["subject"] for m in gateway.sent_messages)


class FailingBookingAutomationPort(BookingAutomationPort):
    @override
    def list_pending_expired(self, cutoff_utc: datetime) -> list[str]:
        return ["book-failed", "book-success", "book-gone"]

    @override
    def list_confirmed_ready(self, cutoff_utc: datetime) -> list[str]:
        return []

    @override
    def list_unreminded_upcoming(self, start_cutoff: datetime, end_cutoff: datetime) -> list[str]:
        return []

    @override
    def cancel_expired(self, booking_id: str, reason: str) -> bool:
        if booking_id == "book-failed":
            msg = "Database connection timed out for this item"
            raise RuntimeError(msg)
        # "book-gone" was handled by another run in the meantime
        return booking_id == "book-success"

    @override
    def complete(self, booking_id: str) -> bool:
        return True

    @override
    def claim_reminder(self, booking_id: str) -> bool:
        return True


def test_scheduler_pending_timeout_resilience_per_item() -> None:
    """D13 - P2: Resiliência per-item no scheduler.

    Garante que se uma transição de booking falhar, o lote continue sendo processado
    para os próximos itens, retornando contadores adequados de processados e falhos.
    Bookings já tratados por outra execução são ignorados, sem contar como falha.
    """
    port = FailingBookingAutomationPort()
    scheduler = BookingScheduler(port)

    result = scheduler.run_pending_timeout()

    assert result.processed == 1
    assert result.failed == 1
    assert result.booking_ids == ["book-success"]
    assert result.failed_booking_ids == ["book-failed"]


class TestJobsAreSafeToRunTwice:
    """#53: a second (or overlapping) run must not act on the same booking again."""

    def _scheduler(self, db_session: Session, gateway: InMemoryEmailGateway) -> BookingScheduler:
        notifications = NotificationService(gateway)
        return BookingScheduler(
            SqlAlchemyBookingAutomationPort(db_session, notifications),
            reminder_sender=BookingNotifier(db_session, notifications),
        )

    def test_timeout_releases_slots_and_notifies_both_once(self, db_session: Session) -> None:
        gateway = InMemoryEmailGateway()
        booking = _seed_full_booking(
            db_session, BookingStatus.PENDENTE.value, starts_offset_hours=48
        )
        scheduler = self._scheduler(db_session, gateway)

        first = scheduler.run_pending_timeout()
        # The listing a concurrent run took before the first one committed
        second = scheduler._run(  # noqa: SLF001
            "pending_timeout",
            [booking.id],
            lambda booking_id: scheduler._automation_port.cancel_expired(booking_id, "x"),  # noqa: SLF001
        )

        assert (first.processed, second.processed, second.failed) == (1, 0, 0)
        db_session.refresh(booking)
        assert booking.status == BookingStatus.CANCELADA.value
        assert booking.cancelled_by == "SISTEMA"
        assert booking.cancellation_reason == "AUTO_TIMEOUT_24H"
        for link in booking.slots:
            db_session.refresh(link.slot)
            assert link.slot.status == SlotStatus.DISPONIVEL.value
        assert [m["recipients"] for m in gateway.sent_messages] == [
            ["autostu@t.com"],
            ["autoinst@t.com"],
        ]

    def test_completion_runs_once(self, db_session: Session) -> None:
        booking = _seed_full_booking(
            db_session, BookingStatus.CONFIRMADA.value, starts_offset_hours=-6
        )
        port = SqlAlchemyBookingAutomationPort(db_session)

        assert port.complete(booking.id) is True
        assert port.complete(booking.id) is False

    def test_reminder_is_sent_once(self, db_session: Session) -> None:
        gateway = InMemoryEmailGateway()
        booking = _seed_full_booking(
            db_session, BookingStatus.CONFIRMADA.value, starts_offset_hours=24
        )
        scheduler = self._scheduler(db_session, gateway)

        first = scheduler.run_lesson_reminders()
        port = SqlAlchemyBookingAutomationPort(db_session)

        assert first.processed == 1
        assert port.claim_reminder(booking.id) is False
        assert scheduler.run_lesson_reminders().processed == 0
        assert len(gateway.sent_messages) == 2  # student + instructor, once
