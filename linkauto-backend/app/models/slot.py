from __future__ import annotations

from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditUUIDBase


class SlotStatus(str, Enum):
    DISPONIVEL = "DISPONIVEL"
    RESERVADO = "RESERVADO"
    BLOQUEADO = "BLOQUEADO"


class Slot(AuditUUIDBase):
    __tablename__ = "slots"

    instructor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("instructor_profiles.user_id"), nullable=False, index=True
    )
    starts_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SlotStatus.DISPONIVEL.value
    )

    __table_args__ = (
        Index("ix_slots_instructor_starts", "instructor_id", "starts_at"),
    )
