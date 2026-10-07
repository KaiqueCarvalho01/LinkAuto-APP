"""Instructor availability slot model and status enum."""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import Index, String
from sqlmodel import Field

from app.models.base import AuditUUIDBase


class SlotStatus(StrEnum):
    """Availability of a slot: open for booking, reserved by a booking, or blocked."""

    DISPONIVEL = "DISPONIVEL"
    RESERVADO = "RESERVADO"
    BLOQUEADO = "BLOQUEADO"


class Slot(AuditUUIDBase, table=True):
    """Time window of an instructor's agenda that students can book (``slots`` table)."""

    __tablename__ = "slots"
    __table_args__ = (Index("ix_slots_instructor_starts", "instructor_id", "starts_at"),)

    instructor_id: str = Field(
        sa_type=String(36), foreign_key="instructor_profiles.user_id", index=True
    )
    starts_at: datetime
    ends_at: datetime
    status: str = Field(default=SlotStatus.DISPONIVEL.value, sa_type=String(20))
