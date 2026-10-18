"""Which instructors students can see slots of and book (RN01)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import col, or_, select

from app.models.user import DetranStatus, InstructorProfile, User

if TYPE_CHECKING:
    from sqlmodel import Session


def find_bookable_instructor(db: Session, instructor_ref: str) -> InstructorProfile | None:
    """Return the instructor profile behind a public slug or user ID, if they can be booked.

    Bookable means the same as publicly visible in search and on profile pages: a
    DETRAN-approved, active instructor profile of an active account. Pending, rejected and
    paused instructors, and deactivated accounts, give ``None``.
    """
    return db.exec(
        select(InstructorProfile)
        .join(User, col(User.id) == col(InstructorProfile.user_id))
        .where(
            or_(
                col(InstructorProfile.slug) == instructor_ref,
                col(InstructorProfile.user_id) == instructor_ref,
            ),
            col(InstructorProfile.detran_status) == DetranStatus.APROVADO.value,
            col(InstructorProfile.is_active).is_(True),
            col(User.is_active).is_(True),
        )
    ).first()
