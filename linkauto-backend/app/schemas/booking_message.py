"""Schemas for booking chat messages."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.datetime import UtcDateTime


class BookingMessageCreateRequest(BaseModel):
    """Payload to post a non-empty message to a booking's conversation."""

    content: str = Field(..., min_length=1)


class MessageResource(BaseModel):
    """Message posted in a booking's conversation, with its sender and UTC creation time."""

    id: str
    booking_id: str
    sender_id: str
    content: str
    created_at: UtcDateTime

    model_config = {"from_attributes": True}
