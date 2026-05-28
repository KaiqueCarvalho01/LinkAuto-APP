from datetime import datetime, timedelta, timezone

import pytest

from app.domain.booking import BookingStatus
from app.models.booking import Booking, CancelledBy
from app.models.slot import Slot, SlotStatus
from app.models.user import (
    DetranStatus, InstructorProfile, StudentProfile, User, UserRole,
)
from app.services.booking_service import (
    BookingService, PenalizedStudentError, SlotValidationError,
)


def _seed_users(db_session):
    instructor = User(id="inst-001", email="inst@test.com", password_hash="h", roles=[UserRole.INSTRUTOR.value])
    inst_profile = InstructorProfile(user_id="inst-001", full_name="Inst", phone="1", city="C", state="SP", detran_status=DetranStatus.APROVADO)
    student = User(id="stu-001", email="stu@test.com", password_hash="h", roles=[UserRole.ALUNO.value])
    stu_profile = StudentProfile(user_id="stu-001", full_name="Stu", phone="2", city="C", state="SP")
    db_session.add_all([instructor, inst_profile, student, stu_profile])
    db_session.flush()


def _create_consecutive_slots(db_session, instructor_id, count=2, base_offset_hours=2):
    now = datetime.now(timezone.utc)
    base = now + timedelta(hours=base_offset_hours)
    slots = []
    for i in range(count):
        s = Slot(
            instructor_id=instructor_id,
            starts_at=base + timedelta(hours=i),
            ends_at=base + timedelta(hours=i + 1),
            status=SlotStatus.DISPONIVEL.value,
        )
        db_session.add(s)
        slots.append(s)
    db_session.flush()
    return slots


class TestBookingServiceCreate:
    def test_creates_booking_with_2_consecutive_slots(self, db_session):
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001", count=2)
        service = BookingService(db_session)

        booking = service.create_booking(
            student_id="stu-001",
            instructor_id="inst-001",
            slot_ids=[s.id for s in slots],
        )

        assert booking.status == BookingStatus.PENDENTE.value
        assert len(booking.slots) == 2
        for s in slots:
            db_session.refresh(s)
            assert s.status == SlotStatus.RESERVADO.value

    def test_rejects_less_than_2_slots(self, db_session):
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001", count=1)
        service = BookingService(db_session)

        with pytest.raises(SlotValidationError, match="minimum 2"):
            service.create_booking("stu-001", "inst-001", [slots[0].id])

    def test_rejects_non_consecutive_slots(self, db_session):
        _seed_users(db_session)
        now = datetime.now(timezone.utc) + timedelta(hours=2)
        s1 = Slot(instructor_id="inst-001", starts_at=now, ends_at=now + timedelta(hours=1), status=SlotStatus.DISPONIVEL.value)
        s2 = Slot(instructor_id="inst-001", starts_at=now + timedelta(hours=3), ends_at=now + timedelta(hours=4), status=SlotStatus.DISPONIVEL.value)
        db_session.add_all([s1, s2])
        db_session.flush()
        service = BookingService(db_session)

        with pytest.raises(SlotValidationError, match="consecutive"):
            service.create_booking("stu-001", "inst-001", [s1.id, s2.id])

    def test_rejects_penalized_student(self, db_session):
        _seed_users(db_session)
        from app.services.penalty_service import PenaltyService
        PenaltyService(db_session).apply_penalty("stu-001", "test penalty")
        slots = _create_consecutive_slots(db_session, "inst-001")
        service = BookingService(db_session)

        with pytest.raises(PenalizedStudentError):
            service.create_booking("stu-001", "inst-001", [s.id for s in slots])


class TestBookingServiceConfirm:
    def test_confirms_pending_booking(self, db_session):
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001")
        service = BookingService(db_session)
        booking = service.create_booking("stu-001", "inst-001", [s.id for s in slots])

        confirmed = service.confirm_booking(booking.id, "inst-001")

        assert confirmed.status == BookingStatus.CONFIRMADA.value
        assert confirmed.confirmed_at is not None


class TestBookingServiceCancel:
    def test_cancel_with_24h_notice_no_penalty(self, db_session):
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001", base_offset_hours=48)
        service = BookingService(db_session)
        booking = service.create_booking("stu-001", "inst-001", [s.id for s in slots])
        service.confirm_booking(booking.id, "inst-001")

        cancelled = service.cancel_booking(booking.id, "stu-001", "ALUNO")

        assert cancelled.status == BookingStatus.CANCELADA.value
        from app.services.penalty_service import PenaltyService
        assert PenaltyService(db_session).is_penalized("stu-001") is False

    def test_cancel_within_24h_applies_penalty(self, db_session):
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001", base_offset_hours=2)
        service = BookingService(db_session)
        booking = service.create_booking("stu-001", "inst-001", [s.id for s in slots])
        service.confirm_booking(booking.id, "inst-001")

        cancelled = service.cancel_booking(booking.id, "stu-001", "ALUNO")

        assert cancelled.status == BookingStatus.CANCELADA.value
        from app.services.penalty_service import PenaltyService
        assert PenaltyService(db_session).is_penalized("stu-001") is True
