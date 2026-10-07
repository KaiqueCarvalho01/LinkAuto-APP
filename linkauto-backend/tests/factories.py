"""Helpers that seed valid rows, so tests satisfy the foreign keys SQLite now enforces."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.core.config import get_settings
from app.core.security import create_access_token
from app.models import DetranStatus, InstructorProfile, StudentProfile, User, UserRole

if TYPE_CHECKING:
    from sqlmodel import Session


def seed_student(db: Session, user_id: str, **profile: Any) -> StudentProfile:  # noqa: ANN401
    """Insert (or reuse) a student account and profile with the given ID."""
    existing = db.get(StudentProfile, user_id)
    if existing is not None:
        return existing
    if db.get(User, user_id) is None:
        db.add(
            User(
                id=user_id,
                email=f"{user_id}@seed.test",
                password_hash="h",
                roles=[UserRole.ALUNO.value],
            )
        )
        db.flush()
    student = StudentProfile(user_id=user_id, **profile)
    db.add(student)
    db.flush()
    return student


def seed_instructor(db: Session, user_id: str, **profile: Any) -> InstructorProfile:  # noqa: ANN401
    """Insert (or reuse) an approved instructor account and profile with the given ID."""
    existing = db.get(InstructorProfile, user_id)
    if existing is not None:
        return existing
    if db.get(User, user_id) is None:
        db.add(
            User(
                id=user_id,
                email=f"{user_id}@seed.test",
                password_hash="h",
                roles=[UserRole.INSTRUTOR.value],
            )
        )
        db.flush()
    profile.setdefault("detran_status", DetranStatus.APROVADO)
    instructor = InstructorProfile(user_id=user_id, **profile)
    db.add(instructor)
    db.flush()
    return instructor


def seed_participants(db: Session, student_id: str, instructor_id: str) -> None:
    """Insert the student and instructor a booking refers to."""
    seed_student(db, student_id)
    seed_instructor(db, instructor_id)


def seed_admin(db: Session, user_id: str = "admin-1") -> User:
    """Insert (or reuse) an active ADMIN account with the given ID."""
    user = db.get(User, user_id)
    if user is None:
        user = User(
            id=user_id,
            email=f"{user_id}@seed.test",
            password_hash="h",
            roles=[UserRole.ADMIN.value],
        )
        db.add(user)
        db.flush()
    return user


def auth_headers(user: User) -> dict[str, str]:
    """Return a bearer header with an access token for the stored user."""
    token = create_access_token(user.id, settings=get_settings(), roles=list(user.roles))
    return {"Authorization": f"Bearer {token}"}


def admin_headers(db: Session, user_id: str = "admin-1") -> dict[str, str]:
    """Seed an admin account and return its bearer header."""
    return auth_headers(seed_admin(db, user_id))
