from app.core.config import get_settings
from app.core.security import create_access_token
from app.models.user import DetranStatus, InstructorProfile, User, UserRole


def _create_token_for(user_id: str, roles: list[str]) -> str:
    settings = get_settings()
    return create_access_token(subject=user_id, roles=roles, settings=settings)


class TestAdminStatsContract:
    def test_admin_stats_endpoint_success_for_admin(self, client, db_session):
        # Create an admin user
        admin = User(id="admin-stat-user", email="admin@stats.com", password_hash="h", roles=[UserRole.ADMIN.value])
        # Create an instructor
        inst = User(id="inst-stat-user", email="inst@stats.com", password_hash="h", roles=[UserRole.INSTRUTOR.value])
        prof = InstructorProfile(
            user_id="inst-stat-user", full_name="Inst 1", phone="1", city="Mogi Mirim", state="SP",
            detran_status=DetranStatus.PENDENTE.value, is_active=True,
        )
        db_session.add_all([admin, inst, prof])
        db_session.commit()

        token = _create_token_for(admin.id, [UserRole.ADMIN.value])
        resp = client.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        data = body["data"]
        assert "total_instructors" in data
        assert "pending_instructors" in data
        assert "approved_instructors" in data
        assert "rejected_instructors" in data
        assert "total_students" in data
        assert "total_bookings" in data
        assert data["pending_instructors"] >= 1

    def test_admin_stats_forbidden_for_non_admin(self, client, db_session):
        student = User(id="student-stat-user", email="stud@stats.com", password_hash="h", roles=[UserRole.ALUNO.value])
        db_session.add(student)
        db_session.commit()

        token = _create_token_for(student.id, [UserRole.ALUNO.value])
        resp = client.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 403

    def test_admin_stats_unauthorized_without_token(self, client):
        resp = client.get("/api/v1/admin/stats")
        assert resp.status_code == 401
