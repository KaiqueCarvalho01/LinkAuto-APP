from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.models.booking import StudentPenalty
from app.models.user import StudentProfile, User, UserRole
from app.services.penalty_service import PenaltyService

if TYPE_CHECKING:
    from sqlmodel import Session


def _seed_student(db_session: Session, student_id: str = "stu-001") -> str:
    user = User(
        id=student_id,
        email=f"{student_id}@test.com",
        password_hash="fakehash",
        roles=[UserRole.ALUNO.value],
    )
    profile = StudentProfile(
        user_id=student_id,
        full_name="Test Student",
        phone="11888888888",
        city="Mogi Mirim",
        state="SP",
    )
    db_session.add_all([user, profile])
    db_session.flush()
    return student_id


class TestPenaltyService:
    def test_no_active_penalty(self, db_session: Session) -> None:
        student_id = _seed_student(db_session)
        service = PenaltyService(db_session)
        assert service.is_penalized(student_id) is False

    def test_active_penalty_blocks(self, db_session: Session) -> None:
        student_id = _seed_student(db_session)
        service = PenaltyService(db_session)
        service.apply_penalty(student_id, reason="Late cancellation RN04")
        assert service.is_penalized(student_id) is True

    def test_expired_penalty_does_not_block(self, db_session: Session) -> None:
        student_id = _seed_student(db_session)
        penalty = StudentPenalty(
            student_id=student_id,
            blocked_until=datetime.now(UTC) - timedelta(days=1),
            reason="Old penalty",
        )
        db_session.add(penalty)
        db_session.flush()

        service = PenaltyService(db_session)
        assert service.is_penalized(student_id) is False
