"""Request and response schemas for booking reviews."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.datetime import UtcDateTime


class ReviewCreateRequest(BaseModel):
    """Payload to review a booking: rating from 1 to 5 and optional comment (max 1000 chars)."""

    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(None, max_length=1000)


class ReviewResource(BaseModel):
    """Review left by a user (reviewer) about another user (reviewed) for a booking."""

    id: str
    booking_id: str
    reviewer_id: str
    reviewed_id: str
    rating: int
    comment: str | None
    created_at: UtcDateTime
    updated_at: UtcDateTime

    model_config = {"from_attributes": True}
