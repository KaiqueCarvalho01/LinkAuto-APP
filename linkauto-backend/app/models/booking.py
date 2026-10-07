"""Booking, booking-slot association and student penalty models."""

from __future__ import annotations

from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditUUIDBase


class CancelledBy(StrEnum):
    """Who cancelled a booking: the student, the instructor or the system (automation)."""

    ALUNO = "ALUNO"
    INSTRUTOR = "INSTRUTOR"
    SISTEMA = "SISTEMA"


class Booking(AuditUUIDBase):
    """Driving lesson booked by a student with an instructor (``bookings`` table).

    ``status`` moves PENDENTE -> CONFIRMADA -> REALIZADA, or to CANCELADA. Indexed by
    (student_id, status) and (instructor_id, status).
    """

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
    confirmed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_by: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reminder_sent: Mapped[bool] = mapped_column(nullable=False, default=False)

    slots = relationship("BookingSlot", back_populates="booking", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_bookings_student_status", "student_id", "status"),
        Index("ix_bookings_instructor_status", "instructor_id", "status"),
    )


class BookingSlot(AuditUUIDBase):
    """Association between a booking and one of its reserved slots (``booking_slots``).

    ``slot_id`` is unique, so a slot can belong to at most one booking; rows are deleted
    with their booking or slot.
    """

    __tablename__ = "booking_slots"

    booking_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False
    )
    slot_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("slots.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    booking = relationship("Booking", back_populates="slots")
    slot = relationship("Slot", lazy="joined")

    __table_args__ = (Index("ix_booking_slots_unique", "booking_id", "slot_id", unique=True),)


class StudentPenalty(AuditUUIDBase):
    """Temporary block on a student's bookings, active until ``blocked_until``."""

    __tablename__ = "student_penalties"

    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("student_profiles.user_id"), nullable=False, index=True
    )
    blocked_until: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
