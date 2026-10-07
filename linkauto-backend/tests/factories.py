"""Helpers that seed valid rows, so tests satisfy the foreign keys SQLite now enforces."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

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
