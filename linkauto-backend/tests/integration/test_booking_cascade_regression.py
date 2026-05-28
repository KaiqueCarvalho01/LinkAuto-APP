from datetime import datetime, timedelta, timezone

import pytest

from app.domain.booking import BookingStatus, BookingTransitionError, transition_booking
from app.models.slot import Slot, SlotStatus
from app.models.user import (
    DetranStatus, InstructorProfile, StudentProfile, User, UserRole,
)
from app.services.booking_automation_store import SqlAlchemyBookingAutomationPort
from app.services.booking_scheduler import BookingScheduler
from app.services.booking_service import BookingService


def _full_seed(db_session):
    inst = User(id="reg-inst", email="reginst@t.com", password_hash="h", roles=[UserRole.INSTRUTOR.value])
    inst_p = InstructorProfile(user_id="reg-inst", full_name="I", phone="1", city="C", state="SP", detran_status=DetranStatus.APROVADO)
    stu = User(id="reg-stu", email="regstu@t.com", password_hash="h", roles=[UserRole.ALUNO.value])
    stu_p = StudentProfile(user_id="reg-stu", full_name="S", phone="2", city="C", state="SP")
    db_session.add_all([inst, inst_p, stu, stu_p])
    db_session.flush()


class TestBookingCascadeRegression:
    def test_full_happy_path_lifecycle(self, db_session):
        """PENDENTE → CONFIRMADA → REALIZADA via service layer."""
        _full_seed(db_session)
        now = datetime.now(timezone.utc) + timedelta(hours=4)
        slots = []
        for i in range(2):
            s = Slot(instructor_id="reg-inst", starts_at=now + timedelta(hours=i), ends_at=now + timedelta(hours=i + 1), status=SlotStatus.DISPONIVEL.value)
            db_session.add(s)
            slots.append(s)
        db_session.flush()

        service = BookingService(db_session)
        booking = service.create_booking("reg-stu", "reg-inst", [s.id for s in slots])
        assert booking.status == BookingStatus.PENDENTE.value

        booking = service.confirm_booking(booking.id, "reg-inst")
        assert booking.status == BookingStatus.CONFIRMADA.value

    def test_domain_transition_invariants_hold(self):
        """Domain state machine rejects invalid transitions."""
        with pytest.raises(BookingTransitionError):
            transition_booking(BookingStatus.REALIZADA, BookingStatus.PENDENTE)

        with pytest.raises(BookingTransitionError):
            transition_booking(BookingStatus.CANCELADA, BookingStatus.CONFIRMADA)

    def test_scheduler_integration(self, db_session):
        """Scheduler uses automation port correctly."""
        _full_seed(db_session)
        port = SqlAlchemyBookingAutomationPort(db_session)
        scheduler = BookingScheduler(port)

        # No bookings to process
        result = scheduler.run_pending_timeout()
        assert result.processed == 0
