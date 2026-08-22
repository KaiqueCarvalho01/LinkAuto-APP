from app.models.booking import Booking
from app.models.user import DetranStatus, InstructorProfile, StudentProfile, User, UserRole
from app.services.admin_stats_service import AdminStatsService


def _seed_stats_data(db_session):
    # 2 Approved instructors, 1 Pending, 1 Rejected
    for i, status in enumerate([
        DetranStatus.APROVADO,
        DetranStatus.APROVADO,
        DetranStatus.PENDENTE,
        DetranStatus.REJEITADO,
    ]):
        uid = f"inst-stat-{i}"
        u = User(id=uid, email=f"inst{i}@stat.com", password_hash="h", roles=[UserRole.INSTRUTOR.value])
        p = InstructorProfile(
            user_id=uid, full_name=f"Inst {i}", phone="1", city="Mogi Mirim", state="SP",
            detran_status=status.value, is_active=True,
        )
        db_session.add_all([u, p])

    # 3 Students
    for i in range(3):
        uid = f"student-stat-{i}"
        u = User(id=uid, email=f"stud{i}@stat.com", password_hash="h", roles=[UserRole.ALUNO.value])
        sp = StudentProfile(user_id=uid, full_name=f"Student {i}", phone="1", city="Mogi Mirim", state="SP")
        db_session.add_all([u, sp])

    # 2 Bookings
    b1 = Booking(id="b-stat-1", student_id="student-stat-0", instructor_id="inst-stat-0", status="PENDENTE")
    b2 = Booking(id="b-stat-2", student_id="student-stat-1", instructor_id="inst-stat-1", status="CONFIRMADA")
    db_session.add_all([b1, b2])

    db_session.flush()


class TestAdminStatsService:
    def test_get_admin_stats_aggregation(self, db_session):
        _seed_stats_data(db_session)
        service = AdminStatsService(db_session)

        stats = service.get_stats()

        assert stats.total_instructors == 4
        assert stats.approved_instructors == 2
        assert stats.pending_instructors == 1
        assert stats.rejected_instructors == 1
        assert stats.total_students == 3
        assert stats.total_bookings == 2
