from __future__ import annotations

from decimal import Decimal
from enum import Enum

from sqlalchemy import Boolean, Enum as SqlEnum, ForeignKey, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditTimestampsMixin, AuditUUIDBase


class UserRole(str, Enum):
    ALUNO = "ALUNO"
    INSTRUTOR = "INSTRUTOR"
    ADMIN = "ADMIN"


class LicenseType(str, Enum):
    NENHUMA = "NENHUMA"
    A = "A"
    B = "B"
    AB = "AB"
    C = "C"
    D = "D"
    E = "E"
    EM_PROCESSO = "EM_PROCESSO"


class DetranStatus(str, Enum):
    PENDENTE = "PENDENTE"
    APROVADO = "APROVADO"
    REJEITADO = "REJEITADO"


class User(AuditUUIDBase):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    roles: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    student_profile: Mapped[StudentProfile | None] = relationship(
        "StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    instructor_profile: Mapped[InstructorProfile | None] = relationship(
        "InstructorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class StudentProfile(AuditTimestampsMixin):
    __tablename__ = "student_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    license_type: Mapped[LicenseType] = mapped_column(
        SqlEnum(LicenseType), nullable=False, default=LicenseType.NENHUMA
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="student_profile")


class InstructorProfile(AuditTimestampsMixin):
    __tablename__ = "instructor_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    specialties: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    price_per_hour: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    detran_status: Mapped[DetranStatus] = mapped_column(
        SqlEnum(DetranStatus), nullable=False, default=DetranStatus.PENDENTE, index=True
    )
    action_radius_km: Mapped[int] = mapped_column(nullable=False, default=10)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    rating_avg: Mapped[float] = mapped_column(nullable=False, default=0.0)
    rating_count: Mapped[int] = mapped_column(nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped[User] = relationship("User", back_populates="instructor_profile")
