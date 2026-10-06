"""Student booking penalties for late cancellations (RN04)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.models.booking import StudentPenalty

if TYPE_CHECKING:
    from sqlmodel import Session

PENALTY_DAYS = 7


class PenaltyService:
    """Check and apply RN04 penalties that block a student from booking."""

    def __init__(self, db: Session) -> None:
        """Store the DB session used to read and write student penalties."""
        self._db = db

    def is_penalized(self, student_id: str) -> bool:
        """Return whether the student has a penalty still in effect."""
        now = datetime.now(UTC)
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
        """Block the student from booking for 7 days from now and flush the penalty."""
        penalty = StudentPenalty(
            student_id=student_id,
            blocked_until=datetime.now(UTC) + timedelta(days=PENALTY_DAYS),
            reason=reason,
        )
        self._db.add(penalty)
        self._db.flush()
        return penalty
