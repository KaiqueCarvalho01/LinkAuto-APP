"""Chat message model attached to a booking."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditUUIDBase


class BookingMessage(AuditUUIDBase):
    """Message sent by a user within a booking's conversation (``booking_messages`` table)."""

    __tablename__ = "booking_messages"

    booking_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (Index("ix_booking_messages_booking_created", "booking_id", "created_at"),)
