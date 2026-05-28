from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.datetime import UtcDateTime


class BookingMessageCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResource(BaseModel):
    id: str
    booking_id: str
    sender_id: str
    content: str
    created_at: UtcDateTime

    model_config = {"from_attributes": True}
