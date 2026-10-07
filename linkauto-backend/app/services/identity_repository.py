"""Database-backed repository for user accounts, profiles and instructor documents."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlmodel import col, func, select

from app.core.slug import generate_profile_slug
from app.models import (
    DetranStatus,
    InstructorDocument,
    InstructorProfile,
    LicenseType,
    StudentProfile,
    User,
    UserRole,
)
from app.models.base import utc_now

if TYPE_CHECKING:
    from collections.abc import Iterable

    from sqlmodel import Session

ALLOWED_ROLES = {role.value for role in UserRole}


class UserNotFoundError(ValueError):
    """Raised when a user (or the instructor profile being looked up) does not exist."""


class DuplicateEmailError(ValueError):
    """Raised when registering an email that already belongs to an account."""


@dataclass(frozen=True, slots=True)
class InstructorPage:
    """A page of instructor accounts with the total number of matches."""

    items: list[User]
    total: int


def normalize_email(email: str) -> str:
    """Return the canonical form of an email address (trimmed, lowercased)."""
    return email.strip().lower()


def serialize_student_profile(profile: StudentProfile) -> dict[str, Any]:
    """Return the private (owner/admin) view of a student profile."""
    return {
        "full_name": profile.full_name,
        "phone": profile.phone,
        "city": profile.city,
        "state": profile.state,
        "license_type": LicenseType(profile.license_type).value,
        "avatar_url": profile.avatar_url,
    }


def serialize_instructor_profile(profile: InstructorProfile) -> dict[str, Any]:
    """Return the private (owner/admin) view of an instructor profile."""
    return {
        "full_name": profile.full_name,
        "phone": profile.phone,
        "city": profile.city,
        "state": profile.state,
        "bio": profile.bio,
        "specialties": list(profile.specialties or []),
        "price_per_hour": float(profile.price_per_hour)
        if profile.price_per_hour is not None
        else None,
        "avatar_url": profile.avatar_url,
        "detran_status": DetranStatus(profile.detran_status).value,
        "action_radius_km": profile.action_radius_km,
        "latitude": profile.latitude,
        "longitude": profile.longitude,
        "rating_avg": profile.rating_avg,
        "rating_count": profile.rating_count,
        "is_active": profile.is_active,
    }


class IdentityRepository:
    """Read and write users, profiles and instructor documents through a DB session.

    Methods only ``flush``; the caller (request handler) owns the transaction and commits.
    """

    def __init__(self, session: Session) -> None:
        """Bind the repository to a session."""
        self._db = session

    # --- users -----------------------------------------------------------------------------

    def create_user(self, email: str, password_hash: str, roles: Iterable[str]) -> User:
        """Create an active user with default profiles for its ALUNO/INSTRUTOR roles.

        Raises ``ValueError`` when no role is given or a role is unsupported, and
        ``DuplicateEmailError`` when the email is already registered.
        """
        normalized_email = normalize_email(email)
        role_list = sorted(set(roles))
        if not role_list:
            msg = "At least one role is required."
            raise ValueError(msg)
        invalid_roles = sorted(set(role_list) - ALLOWED_ROLES)
        if invalid_roles:
            msg = f"Unsupported role(s): {', '.join(invalid_roles)}"
            raise ValueError(msg)
        if self.get_user_by_email(normalized_email) is not None:
            msg = "Email already registered."
            raise DuplicateEmailError(msg)

        user = User(email=normalized_email, password_hash=password_hash, roles=role_list)
        self._db.add(user)
        if UserRole.ALUNO.value in role_list:
            user.student_profile = StudentProfile(user_id=user.id)
        if UserRole.INSTRUTOR.value in role_list:
            user.instructor_profile = InstructorProfile(user_id=user.id)
        self._db.flush()
        return user

    def get_user(self, user_id: str) -> User | None:
        """Return the user with the given ID, or ``None``."""
        return self._db.get(User, user_id)

    def get_user_by_email(self, email: str) -> User | None:
        """Return the user with the given (case-insensitive) email, or ``None``."""
        return self._db.exec(select(User).where(col(User.email) == normalize_email(email))).first()

    def update_profile(self, user_id: str, payload: dict[str, Any]) -> User:
        """Apply ``student_profile``/``instructor_profile`` partial updates from ``payload``.

        Raises ``UserNotFoundError`` if the user does not exist and ``ValueError`` if it lacks
        the role matching a submitted profile.
        """
        user = self.get_user(user_id)
        if user is None:
            msg = "User not found."
            raise UserNotFoundError(msg)

        student_update = payload.get("student_profile")
        if student_update is not None:
            if UserRole.ALUNO.value not in user.roles:
                msg = "User does not have ALUNO role."
                raise ValueError(msg)
            if user.student_profile is None:
                user.student_profile = StudentProfile(user_id=user.id)
            _apply_student_update(user.student_profile, student_update)

        instructor_update = payload.get("instructor_profile")
        if instructor_update is not None:
            if UserRole.INSTRUTOR.value not in user.roles:
                msg = "User does not have INSTRUTOR role."
                raise ValueError(msg)
            if user.instructor_profile is None:
                user.instructor_profile = InstructorProfile(user_id=user.id)
            _apply_instructor_update(user.instructor_profile, instructor_update)

        user.updated_at = utc_now()
        self._db.flush()
        return user

    # --- instructors -----------------------------------------------------------------------

    def list_instructors(
        self, *, status: str | None = None, page: int = 1, page_size: int = 20
    ) -> InstructorPage:
        """Return a page of users with an instructor profile, oldest first.

        Optionally filtered by DETRAN status.
        """
        stmt = select(User).join(InstructorProfile, col(InstructorProfile.user_id) == col(User.id))
        count_stmt = select(func.count()).select_from(InstructorProfile)
        if status:
            stmt = stmt.where(col(InstructorProfile.detran_status) == status)
            count_stmt = count_stmt.where(col(InstructorProfile.detran_status) == status)
        total = self._db.exec(count_stmt).one()
        items = self._db.exec(
            stmt.order_by(col(User.created_at), col(User.id))
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return InstructorPage(items=list(items), total=total)

    def list_public_instructors(self) -> list[InstructorProfile]:
        """Return active, DETRAN-approved instructor profiles of active accounts."""
        return list(
            self._db.exec(
                select(InstructorProfile)
                .join(User, col(User.id) == col(InstructorProfile.user_id))
                .where(
                    col(InstructorProfile.detran_status) == DetranStatus.APROVADO.value,
                    col(InstructorProfile.is_active).is_(True),
                    col(User.is_active).is_(True),
                )
                .order_by(col(InstructorProfile.created_at))
            ).all()
        )

    def ensure_instructor_slug(self, profile: InstructorProfile) -> str:
        """Return the profile's public slug, generating and storing one if missing."""
        if not profile.slug:
            profile.slug = generate_profile_slug(
                profile.full_name, profile.city, default_prefix="instrutor"
            )
            self._db.flush()
        return profile.slug

    def review_instructor(
        self, instructor_id: str, *, status: str, reviewed_by: str, reason: str | None = None
    ) -> User:
        """Set the instructor's DETRAN status and record the review on all their documents.

        Raises ``UserNotFoundError`` if the user does not exist or has no instructor profile.
        """
        user = self.get_user(instructor_id)
        if user is None or user.instructor_profile is None:
            msg = "Instructor not found."
            raise UserNotFoundError(msg)

        now = utc_now()
        user.instructor_profile.detran_status = DetranStatus(status)
        user.updated_at = now
        for document in self.list_documents(instructor_id):
            document.reviewed_by = _existing_user_id(self._db, reviewed_by)
            document.reviewed_at = now
            document.review_status = status
            document.review_reason = reason
        self._db.flush()
        return user

    # --- instructor documents --------------------------------------------------------------

    def add_instructor_document(
        self, instructor_id: str, *, detran_credential_url: str, criminal_record_url: str
    ) -> InstructorDocument:
        """Register a new set of validation documents for an instructor.

        Raises ``UserNotFoundError`` if the user does not exist or has no instructor profile.
        """
        user = self.get_user(instructor_id)
        if user is None or user.instructor_profile is None:
            msg = "Instructor not found."
            raise UserNotFoundError(msg)

        document = InstructorDocument(
            instructor_id=instructor_id,
            detran_credential_url=detran_credential_url,
            criminal_record_url=criminal_record_url,
            uploaded_at=utc_now(),
        )
        self._db.add(document)
        self._db.flush()
        return document

    def list_documents(self, instructor_id: str) -> list[InstructorDocument]:
        """Return the documents uploaded by the given instructor, oldest first."""
        return list(
            self._db.exec(
                select(InstructorDocument)
                .where(col(InstructorDocument.instructor_id) == instructor_id)
                .order_by(col(InstructorDocument.uploaded_at))
            ).all()
        )

    def purge_instructor_documents(self, instructor_id: str) -> list[str]:
        """Delete the instructor's document records and return their storage keys."""
        purged_keys: list[str] = []
        for document in self.list_documents(instructor_id):
            purged_keys.extend(
                key for key in (document.detran_credential_url, document.criminal_record_url) if key
            )
            self._db.delete(document)
        self._db.flush()
        return purged_keys


_STUDENT_FIELDS = ("full_name", "phone", "city", "state", "avatar_url")
_INSTRUCTOR_FIELDS = (
    "full_name",
    "phone",
    "city",
    "state",
    "bio",
    "avatar_url",
    "action_radius_km",
    "latitude",
    "longitude",
    "is_active",
)


def _apply_student_update(profile: StudentProfile, update: dict[str, Any]) -> None:
    for field_name in _STUDENT_FIELDS:
        if field_name in update:
            setattr(profile, field_name, update[field_name])
    if "license_type" in update:
        raw = update["license_type"]
        try:
            profile.license_type = LicenseType(raw) if raw is not None else LicenseType.NENHUMA
        except ValueError as exc:
            msg = f"Unsupported license_type: {raw}"
            raise ValueError(msg) from exc


def _apply_instructor_update(profile: InstructorProfile, update: dict[str, Any]) -> None:
    for field_name in _INSTRUCTOR_FIELDS:
        if field_name in update and not (
            update[field_name] is None and field_name in {"action_radius_km", "is_active"}
        ):
            setattr(profile, field_name, update[field_name])
    if "specialties" in update:
        profile.specialties = list(update["specialties"] or [])
    if "price_per_hour" in update:
        price = update["price_per_hour"]
        profile.price_per_hour = Decimal(str(price)) if price is not None else None


def _existing_user_id(db: Session, user_id: str) -> str | None:
    """Return ``user_id`` if it names a stored user (``reviewed_by`` is a foreign key)."""
    return user_id if db.get(User, user_id) is not None else None
