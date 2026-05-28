from datetime import datetime, timedelta, timezone

import pytest

from app.domain.booking import BookingStatus
from app.models.slot import Slot, SlotStatus
from app.models.user import (
    DetranStatus, InstructorProfile, StudentProfile, User, UserRole,
)
from app.services.booking_service import (
    BookingService, PenalizedStudentError, SlotValidationError,
)
from app.services.penalty_service import PenaltyService


def _seed_scenario(db_session):
    inst = User(id="rn-inst", email="rninst@t.com", password_hash="h", roles=[UserRole.INSTRUTOR.value])
    inst_p = InstructorProfile(user_id="rn-inst", full_name="I", phone="1", city="C", state="SP", detran_status=DetranStatus.APROVADO)
    stu = User(id="rn-stu", email="rnstu@t.com", password_hash="h", roles=[UserRole.ALUNO.value])
    stu_p = StudentProfile(user_id="rn-stu", full_name="S", phone="2", city="C", state="SP")
    stu2 = User(id="rn-stu2", email="rnstu2@t.com", password_hash="h", roles=[UserRole.ALUNO.value])
    stu2_p = StudentProfile(user_id="rn-stu2", full_name="S2", phone="3", city="C", state="SP")
    db_session.add_all([inst, inst_p, stu, stu_p, stu2, stu2_p])
    db_session.flush()


def _make_slots(db_session, count=3, offset_hours=4):
    now = datetime.now(timezone.utc) + timedelta(hours=offset_hours)
    slots = []
    for i in range(count):
        s = Slot(
            instructor_id="rn-inst",
            starts_at=now + timedelta(hours=i),
            ends_at=now + timedelta(hours=i + 1),
            status=SlotStatus.DISPONIVEL.value,
        )
        db_session.add(s)
        slots.append(s)
    db_session.flush()
    return slots


class TestRN02MinimumSlots:
    def test_2_consecutive_slots_succeeds(self, db_session):
        _seed_scenario(db_session)
        slots = _make_slots(db_session, count=2)
        service = BookingService(db_session)

        booking = service.create_booking("rn-stu", "rn-inst", [s.id for s in slots])
        assert booking.status == BookingStatus.PENDENTE.value

    def test_1_slot_fails(self, db_session):
        _seed_scenario(db_session)
        slots = _make_slots(db_session, count=1)
        service = BookingService(db_session)

        with pytest.raises(SlotValidationError, match="minimum 2"):
            service.create_booking("rn-stu", "rn-inst", [slots[0].id])

    def test_non_consecutive_fails(self, db_session):
        _seed_scenario(db_session)
        now = datetime.now(timezone.utc) + timedelta(hours=10)
        s1 = Slot(instructor_id="rn-inst", starts_at=now, ends_at=now + timedelta(hours=1), status=SlotStatus.DISPONIVEL.value)
        s2 = Slot(instructor_id="rn-inst", starts_at=now + timedelta(hours=3), ends_at=now + timedelta(hours=4), status=SlotStatus.DISPONIVEL.value)
        db_session.add_all([s1, s2])
        db_session.flush()
        service = BookingService(db_session)

        with pytest.raises(SlotValidationError, match="consecutive"):
            service.create_booking("rn-stu", "rn-inst", [s1.id, s2.id])


class TestRN03NoOverlap:
    def test_second_booking_same_slots_fails(self, db_session):
        _seed_scenario(db_session)
        slots = _make_slots(db_session, count=4)
        service = BookingService(db_session)

        service.create_booking("rn-stu", "rn-inst", [slots[0].id, slots[1].id])

        with pytest.raises(SlotValidationError, match="not available"):
            service.create_booking("rn-stu2", "rn-inst", [slots[0].id, slots[1].id])


class TestRN04CancellationPenalty:
    def test_cancel_gt_24h_no_penalty(self, db_session):
        _seed_scenario(db_session)
        slots = _make_slots(db_session, count=2, offset_hours=48)
        service = BookingService(db_session)

        booking = service.create_booking("rn-stu", "rn-inst", [s.id for s in slots])
        service.confirm_booking(booking.id, "rn-inst")
        service.cancel_booking(booking.id, "rn-stu", "ALUNO")

        assert PenaltyService(db_session).is_penalized("rn-stu") is False

    def test_cancel_lt_24h_applies_penalty(self, db_session):
        _seed_scenario(db_session)
        slots = _make_slots(db_session, count=2, offset_hours=2)
        service = BookingService(db_session)

        booking = service.create_booking("rn-stu", "rn-inst", [s.id for s in slots])
        service.confirm_booking(booking.id, "rn-inst")
        service.cancel_booking(booking.id, "rn-stu", "ALUNO")

        assert PenaltyService(db_session).is_penalized("rn-stu") is True


class TestPenalizedStudentBlock:
    def test_penalized_student_cannot_book(self, db_session):
        _seed_scenario(db_session)
        PenaltyService(db_session).apply_penalty("rn-stu", "test")
        slots = _make_slots(db_session, count=2)
        service = BookingService(db_session)

        with pytest.raises(PenalizedStudentError):
            service.create_booking("rn-stu", "rn-inst", [s.id for s in slots])
