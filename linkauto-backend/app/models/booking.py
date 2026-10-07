"""Booking, booking-slot link and student penalty models."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Index, String, Text
from sqlmodel import Field, Relationship

from app.models.base import AuditUUIDBase
from app.models.slot import Slot
from app.models.user import InstructorProfile


class CancelledBy(StrEnum):
    """Who cancelled a booking: student, instructor, system (timeouts) or an admin override."""

    ALUNO = "ALUNO"
    INSTRUTOR = "INSTRUTOR"
    SISTEMA = "SISTEMA"
    ADMIN = "ADMIN"


class Booking(AuditUUIDBase, table=True):
    """Lesson booked by a student with an instructor, spanning one or more slots.

    ``status`` moves PENDENTE -> CONFIRMADA -> REALIZADA, or to CANCELADA. Indexed by
    (student_id, status) and (instructor_id, status).
    """

    __tablename__ = "bookings"
    __table_args__ = (
        Index("ix_bookings_student_status", "student_id", "status"),
        Index("ix_bookings_instructor_status", "instructor_id", "status"),
    )

    student_id: str = Field(sa_type=String(36), foreign_key="student_profiles.user_id", index=True)
    instructor_id: str = Field(
        sa_type=String(36), foreign_key="instructor_profiles.user_id", index=True
    )
    status: str = Field(default="PENDENTE", sa_type=String(20))
    location_description: str | None = Field(default=None, sa_type=Text)
    latitude: Decimal | None = Field(default=None, max_digits=10, decimal_places=7)
    longitude: Decimal | None = Field(default=None, max_digits=10, decimal_places=7)
    confirmed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancelled_by: str | None = Field(default=None, sa_type=String(20))
    cancellation_reason: str | None = Field(default=None, sa_type=Text)
    reminder_sent: bool = False

    slots: list["BookingSlot"] = Relationship(
        back_populates="booking", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    # Read-only: used to show the instructor's public identity alongside the booking
    instructor_profile: InstructorProfile = Relationship(
        sa_relationship_kwargs={"viewonly": True, "lazy": "joined"}
    )


class BookingSlot(AuditUUIDBase, table=True):
    """Link between a booking and one of its slots.

    ``slot_id`` is unique, so a slot can belong to at most one booking; rows are deleted
    with their booking or slot.
    """

    __tablename__ = "booking_slots"
    __table_args__ = (Index("ix_booking_slots_unique", "booking_id", "slot_id", unique=True),)

    booking_id: str = Field(sa_type=String(36), foreign_key="bookings.id", ondelete="CASCADE")
    slot_id: str = Field(
        sa_type=String(36), foreign_key="slots.id", ondelete="CASCADE", unique=True
    )

    booking: Booking = Relationship(back_populates="slots")
    slot: Slot = Relationship(sa_relationship_kwargs={"lazy": "joined"})


class StudentPenalty(AuditUUIDBase, table=True):
    """Booking block applied to a student until ``blocked_until`` (rule RN04)."""

    __tablename__ = "student_penalties"

    student_id: str = Field(sa_type=String(36), foreign_key="student_profiles.user_id", index=True)
    blocked_until: datetime
    reason: str = Field(sa_type=Text)


class BookingStatusOverride(AuditUUIDBase, table=True):
    """Audit trail of an admin forcing a booking's status, with who, when and why.

    ``admin_id`` is deliberately not a foreign key, so the record survives the admin's
    account being deleted.
    """

    __tablename__ = "booking_status_overrides"

    booking_id: str = Field(
        sa_type=String(36), foreign_key="bookings.id", ondelete="CASCADE", index=True
    )
    admin_id: str = Field(sa_type=String(36), index=True)
    from_status: str = Field(sa_type=String(20))
    to_status: str = Field(sa_type=String(20))
    reason: str = Field(sa_type=Text)
