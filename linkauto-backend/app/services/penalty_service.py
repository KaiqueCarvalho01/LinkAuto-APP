from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.booking import StudentPenalty

PENALTY_DAYS = 7


class PenaltyService:
    def __init__(self, db: Session):
        self._db = db

    def is_penalized(self, student_id: str) -> bool:
        now = datetime.now(timezone.utc)
        active = (
            self._db.query(StudentPenalty)
            .filter(
                StudentPenalty.student_id == student_id,
                StudentPenalty.blocked_until > now,
            )
            .first()
        )
        return active is not None

    def apply_penalty(self, student_id: str, reason: str) -> StudentPenalty:
        penalty = StudentPenalty(
            student_id=student_id,
            blocked_until=datetime.now(timezone.utc) + timedelta(days=PENALTY_DAYS),
            reason=reason,
        )
        self._db.add(penalty)
        self._db.flush()
        return penalty
