from datetime import datetime, timezone, timedelta
from app.models.booking import Booking, BookingSlot
from app.models.slot import Slot, SlotStatus
from app.models.user import DetranStatus, InstructorProfile, StudentProfile, User, UserRole
from app.services.instructor_stats_service import InstructorStatsService


def _seed_instructor_stats(db_session, instructor_id="inst-stats-1"):
    # Create instructor
    u_inst = User(id=instructor_id, email="inst@statstest.com", password_hash="h", roles=[UserRole.INSTRUTOR.value])
    p_inst = InstructorProfile(
        user_id=instructor_id, full_name="Stats Instructor", phone="1", city="Mogi Mirim", state="SP",
        detran_status=DetranStatus.APROVADO.value, is_active=True,
    )
    db_session.add_all([u_inst, p_inst])

    # Create 2 students
    for s_idx in [1, 2]:
        sid = f"student-stats-{s_idx}"
        u_s = User(id=sid, email=f"s{s_idx}@statstest.com", password_hash="h", roles=[UserRole.ALUNO.value])
        sp = StudentProfile(user_id=sid, full_name=f"Student {s_idx}", phone="1", city="Mogi Mirim", state="SP")
        db_session.add_all([u_s, sp])

    # Create 4 slots for this instructor
    now = datetime.now(timezone.utc)
    slots = []
    for i in range(4):
        slot = Slot(
            id=f"slot-stats-{i}",
            instructor_id=instructor_id,
            starts_at=now + timedelta(hours=i),
            ends_at=now + timedelta(hours=i + 1),
            status=SlotStatus.RESERVADO.value,
        )
        db_session.add(slot)
        slots.append(slot)

    # 1 Realized booking with 2 slots (Student 1) -> 2 hours
    b_realized = Booking(id="b-real-1", student_id="student-stats-1", instructor_id=instructor_id, status="REALIZADA")
    bs1 = BookingSlot(id="bs-1", booking_id="b-real-1", slot_id="slot-stats-0")
    bs2 = BookingSlot(id="bs-2", booking_id="b-real-1", slot_id="slot-stats-1")

    # 1 Pending booking with 2 slots (Student 2)
    b_pending = Booking(id="b-pend-1", student_id="student-stats-2", instructor_id=instructor_id, status="PENDENTE")
    bs3 = BookingSlot(id="bs-3", booking_id="b-pend-1", slot_id="slot-stats-2")
    bs4 = BookingSlot(id="bs-4", booking_id="b-pend-1", slot_id="slot-stats-3")

    db_session.add_all([b_realized, bs1, bs2, b_pending, bs3, bs4])
    db_session.flush()


class TestInstructorStatsService:
    def test_get_instructor_stats(self, db_session):
        inst_id = "inst-stats-1"
        _seed_instructor_stats(db_session, instructor_id=inst_id)
        service = InstructorStatsService(db_session)

        stats = service.get_stats(instructor_id=inst_id)

        assert stats.total_lessons == 1
        assert stats.total_hours == 2
        assert stats.unique_students == 2
        assert stats.pending_bookings == 1
