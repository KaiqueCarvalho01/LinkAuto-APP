"""User account and student/instructor profile models with related enums."""

from decimal import Decimal
from enum import StrEnum
from typing import Optional

from sqlalchemy import JSON, Double, String, event
from sqlalchemy import Enum as SqlEnum
from sqlmodel import Field, Relationship

from app.core.slug import (
    INSTRUCTOR_SLUG_PREFIX,
    STUDENT_SLUG_PREFIX,
    generate_profile_slug,
    is_placeholder_slug,
    placeholder_slug,
)
from app.models.base import AuditTimestampsMixin, AuditUUIDBase


class UserRole(StrEnum):
    """Role of a user account: student (ALUNO), instructor (INSTRUTOR) or administrator."""

    ALUNO = "ALUNO"
    INSTRUTOR = "INSTRUTOR"
    ADMIN = "ADMIN"


class LicenseType(StrEnum):
    """Driver's license category held by a student: none, A-E, AB or in process."""

    NENHUMA = "NENHUMA"
    A = "A"
    B = "B"
    AB = "AB"
    C = "C"
    D = "D"
    E = "E"
    EM_PROCESSO = "EM_PROCESSO"


class DetranStatus(StrEnum):
    """Admin validation status of an instructor's DETRAN credentials."""

    PENDENTE = "PENDENTE"
    APROVADO = "APROVADO"
    REJEITADO = "REJEITADO"


class User(AuditUUIDBase, table=True):
    """User account with unique email, password hash and list of roles (``users`` table).

    Owns at most one student profile and one instructor profile.
    """

    __tablename__ = "users"

    email: str = Field(sa_type=String(255), unique=True, index=True)
    password_hash: str = Field(sa_type=String(255))
    roles: list[str] = Field(default_factory=list, sa_type=JSON)
    is_active: bool = True

    student_profile: Optional["StudentProfile"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"},
    )
    instructor_profile: Optional["InstructorProfile"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"},
    )


class StudentProfile(AuditTimestampsMixin, table=True):
    """Student profile keyed by its user ID, with an optional unique public slug."""

    __tablename__ = "student_profiles"

    user_id: str = Field(
        sa_type=String(36), foreign_key="users.id", ondelete="CASCADE", primary_key=True
    )
    # Set when the profile is created: public profile URLs never change by themselves
    slug: str = Field(
        default_factory=lambda: placeholder_slug(STUDENT_SLUG_PREFIX),
        sa_type=String(150),
        unique=True,
        index=True,
    )
    full_name: str | None = Field(default=None, sa_type=String(255))
    phone: str | None = Field(default=None, sa_type=String(30))
    city: str | None = Field(default=None, sa_type=String(120))
    state: str | None = Field(default=None, sa_type=String(120))
    license_type: LicenseType = Field(default=LicenseType.NENHUMA, sa_type=SqlEnum(LicenseType))
    avatar_url: str | None = Field(default=None, sa_type=String(500))

    user: User = Relationship(back_populates="student_profile")


class InstructorProfile(AuditTimestampsMixin, table=True):
    """Instructor profile keyed by its user ID, with an optional unique public slug.

    Holds public listing data (bio, specialties, hourly price, service radius, location),
    the DETRAN validation status and the aggregated rating.
    """

    __tablename__ = "instructor_profiles"

    user_id: str = Field(
        sa_type=String(36), foreign_key="users.id", ondelete="CASCADE", primary_key=True
    )
    # Set when the profile is created: public profile URLs never change by themselves
    slug: str = Field(
        default_factory=lambda: placeholder_slug(INSTRUCTOR_SLUG_PREFIX),
        sa_type=String(150),
        unique=True,
        index=True,
    )
    full_name: str | None = Field(default=None, sa_type=String(255))
    phone: str | None = Field(default=None, sa_type=String(30))
    city: str | None = Field(default=None, sa_type=String(120))
    state: str | None = Field(default=None, sa_type=String(120))
    bio: str | None = Field(default=None, sa_type=String(2000))
    specialties: list[str] = Field(default_factory=list, sa_type=JSON)
    price_per_hour: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)
    avatar_url: str | None = Field(default=None, sa_type=String(500))
    detran_status: DetranStatus = Field(
        default=DetranStatus.PENDENTE, sa_type=SqlEnum(DetranStatus), index=True
    )
    action_radius_km: int = 10
    latitude: float | None = Field(default=None, sa_type=Double)
    longitude: float | None = Field(default=None, sa_type=Double)
    rating_avg: float = Field(default=0.0, sa_type=Double)
    rating_count: int = 0
    is_active: bool = True

    user: User = Relationship(back_populates="instructor_profile")


def _name_placeholder_slug(profile: StudentProfile | InstructorProfile, prefix: str) -> None:
    """Give a profile a name-based slug the first time it has a name.

    Profiles start with a placeholder slug (``aluno-3f2a``). Once a slug carries a name it
    never changes again, so shared profile links keep working.
    """
    if profile.full_name and is_placeholder_slug(profile.slug, prefix):
        profile.slug = generate_profile_slug(profile.full_name, profile.city, default_prefix=prefix)


@event.listens_for(StudentProfile, "before_insert")
@event.listens_for(StudentProfile, "before_update")
def _name_student_slug(_mapper: object, _connection: object, profile: StudentProfile) -> None:
    _name_placeholder_slug(profile, STUDENT_SLUG_PREFIX)


@event.listens_for(InstructorProfile, "before_insert")
@event.listens_for(InstructorProfile, "before_update")
def _name_instructor_slug(_mapper: object, _connection: object, profile: InstructorProfile) -> None:
    _name_placeholder_slug(profile, INSTRUCTOR_SLUG_PREFIX)
