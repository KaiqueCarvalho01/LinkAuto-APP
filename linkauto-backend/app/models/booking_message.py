"""Chat message model attached to a booking."""

from sqlalchemy import Index, String, Text
from sqlmodel import Field

from app.models.base import AuditUUIDBase


class BookingMessage(AuditUUIDBase, table=True):
    """Message sent by a user within a booking's conversation (``booking_messages`` table)."""

    __tablename__ = "booking_messages"
    __table_args__ = (Index("ix_booking_messages_booking_created", "booking_id", "created_at"),)

    booking_id: str = Field(
        sa_type=String(36), foreign_key="bookings.id", ondelete="CASCADE", index=True
    )
    sender_id: str = Field(
        sa_type=String(36), foreign_key="users.id", ondelete="CASCADE", index=True
    )
    content: str = Field(sa_type=Text)
