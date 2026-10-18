"""Schemas for booking chat messages."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.datetime import UtcDateTime

MAX_MESSAGE_LENGTH = 2000


class BookingMessageCreateRequest(BaseModel):
    """Payload to post a message (1 to 2000 characters) to a booking's conversation."""

    content: str = Field(..., min_length=1, max_length=MAX_MESSAGE_LENGTH)


class MessageResource(BaseModel):
    """Message posted in a booking's conversation, with its sender and UTC creation time."""

    id: str
    booking_id: str
    sender_id: str
    content: str
    created_at: UtcDateTime

    model_config = {"from_attributes": True}
