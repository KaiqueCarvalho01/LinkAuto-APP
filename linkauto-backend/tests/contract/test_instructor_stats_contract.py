from app.core.config import get_settings
from app.core.security import create_access_token
from app.models.user import DetranStatus, InstructorProfile, User, UserRole


def _create_token_for(user_id: str, roles: list[str]) -> str:
    settings = get_settings()
    return create_access_token(subject=user_id, roles=roles, settings=settings)


class TestInstructorStatsContract:
    def test_instructor_stats_success_for_instructor(self, client, db_session):
        inst_id = "contract-inst-stat-id"
        user = User(id=inst_id, email="inst@contractstats.com", password_hash="h", roles=[UserRole.INSTRUTOR.value])
        prof = InstructorProfile(
            user_id=inst_id, full_name="Inst Contract", phone="1", city="Mogi Mirim", state="SP",
            detran_status=DetranStatus.APROVADO.value, is_active=True,
        )
        db_session.add_all([user, prof])
        db_session.commit()

        token = _create_token_for(inst_id, [UserRole.INSTRUTOR.value])
        resp = client.get("/api/v1/instructor/stats", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        data = body["data"]
        assert "total_lessons" in data
        assert "total_hours" in data
        assert "unique_students" in data
        assert "pending_bookings" in data

    def test_instructor_stats_forbidden_for_student(self, client, db_session):
        student_id = "contract-student-id"
        user = User(id=student_id, email="stud@contractstats.com", password_hash="h", roles=[UserRole.ALUNO.value])
        db_session.add(user)
        db_session.commit()

        token = _create_token_for(student_id, [UserRole.ALUNO.value])
        resp = client.get("/api/v1/instructor/stats", headers={"Authorization": f"Bearer {token}"})

        assert resp.status_code == 403

    def test_instructor_stats_unauthorized_without_token(self, client):
        resp = client.get("/api/v1/instructor/stats")
        assert resp.status_code == 401
