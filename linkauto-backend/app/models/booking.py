from __future__ import annotations

from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditUUIDBase


class CancelledBy(str, Enum):
    ALUNO = "ALUNO"
    INSTRUTOR = "INSTRUTOR"
    SISTEMA = "SISTEMA"


class Booking(AuditUUIDBase):
    __tablename__ = "bookings"

    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("student_profiles.user_id"), nullable=False, index=True
    )
    instructor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("instructor_profiles.user_id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDENTE")
    location_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    confirmed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_by: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    slots = relationship("BookingSlot", back_populates="booking", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_bookings_student_status", "student_id", "status"),
        Index("ix_bookings_instructor_status", "instructor_id", "status"),
    )


class BookingSlot(AuditUUIDBase):
    __tablename__ = "booking_slots"

    booking_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False
    )
    slot_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("slots.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    booking = relationship("Booking", back_populates="slots")

    __table_args__ = (
        Index("ix_booking_slots_unique", "booking_id", "slot_id", unique=True),
    )


class StudentPenalty(AuditUUIDBase):
    __tablename__ = "student_penalties"

    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("student_profiles.user_id"), nullable=False, index=True
    )
    blocked_until: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
