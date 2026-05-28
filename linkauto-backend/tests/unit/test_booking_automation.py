from datetime import datetime, timedelta, timezone

from app.domain.booking import BookingStatus
from app.models.booking import Booking
from app.models.slot import Slot, SlotStatus
from app.models.booking import BookingSlot
from app.models.user import (
    DetranStatus, InstructorProfile, StudentProfile, User, UserRole,
)
from app.services.booking_automation_store import SqlAlchemyBookingAutomationPort
from app.services.booking_scheduler import BookingScheduler


def _seed_full_booking(db_session, status, starts_offset_hours, booking_id="book-auto"):
    inst = User(id="auto-inst", email="autoinst@t.com", password_hash="h", roles=[UserRole.INSTRUTOR.value])
    inst_p = InstructorProfile(user_id="auto-inst", full_name="I", phone="1", city="C", state="SP", detran_status=DetranStatus.APROVADO)
    stu = User(id="auto-stu", email="autostu@t.com", password_hash="h", roles=[UserRole.ALUNO.value])
    stu_p = StudentProfile(user_id="auto-stu", full_name="S", phone="2", city="C", state="SP")

    now = datetime.now(timezone.utc)
    base = now + timedelta(hours=starts_offset_hours)
    slot1 = Slot(instructor_id="auto-inst", starts_at=base, ends_at=base + timedelta(hours=1), status=SlotStatus.RESERVADO.value)
    slot2 = Slot(instructor_id="auto-inst", starts_at=base + timedelta(hours=1), ends_at=base + timedelta(hours=2), status=SlotStatus.RESERVADO.value)

    # Set created_at to 48 hours ago for pending timeout testing
    booking = Booking(
        id=booking_id,
        student_id="auto-stu",
        instructor_id="auto-inst",
        status=status,
        created_at=now - timedelta(hours=48),
    )
    db_session.add_all([inst, inst_p, stu, stu_p, slot1, slot2, booking])
    db_session.flush()

    db_session.add_all([
        BookingSlot(booking_id=booking.id, slot_id=slot1.id),
        BookingSlot(booking_id=booking.id, slot_id=slot2.id),
    ])
    db_session.flush()
    return booking


class TestBookingAutomationPort:
    def test_pending_timeout_cancels_old_bookings(self, db_session):
        booking = _seed_full_booking(db_session, BookingStatus.PENDENTE.value, starts_offset_hours=-48)
        port = SqlAlchemyBookingAutomationPort(db_session)
        scheduler = BookingScheduler(port)

        result = scheduler.run_pending_timeout()

        db_session.refresh(booking)
        assert booking.status == BookingStatus.CANCELADA.value
        assert result.processed == 1

    def test_confirmed_completion_after_2h(self, db_session):
        booking = _seed_full_booking(db_session, BookingStatus.CONFIRMADA.value, starts_offset_hours=-6)
        port = SqlAlchemyBookingAutomationPort(db_session)
        scheduler = BookingScheduler(port)

        result = scheduler.run_confirmed_completion()

        db_session.refresh(booking)
        assert booking.status == BookingStatus.REALIZADA.value
        assert result.processed == 1


    def test_lesson_reminder_cron_triggers(self, db_session):
        from app.services.notification_service import NotificationService, InMemoryEmailGateway
        gateway = InMemoryEmailGateway()
        notification_svc = NotificationService(email_gateway=gateway)

        booking = _seed_full_booking(db_session, BookingStatus.CONFIRMADA.value, starts_offset_hours=24, booking_id="book-reminder")
        
        port = SqlAlchemyBookingAutomationPort(db_session)
        scheduler = BookingScheduler(port, notification_service=notification_svc)

        result = scheduler.run_lesson_reminders()

        db_session.refresh(booking)
        assert booking.reminder_sent is True
        assert result.processed == 1
        
        # Verify emails sent to both student and instructor
        assert len(gateway.sent_messages) == 1
        email = gateway.sent_messages[0]
        # Should contain both recipients
        assert "autostu@t.com" in email["recipients"]
        assert "autoinst@t.com" in email["recipients"]
        assert "Lembrete" in email["subject"]
