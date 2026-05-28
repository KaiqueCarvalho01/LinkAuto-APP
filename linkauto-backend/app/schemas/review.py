from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.datetime import UtcDateTime


class ReviewCreateRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(None, max_length=1000)


class ReviewResource(BaseModel):
    id: str
    booking_id: str
    reviewer_id: str
    reviewed_id: str
    rating: int
    comment: str | None
    created_at: UtcDateTime
    updated_at: UtcDateTime

    model_config = {"from_attributes": True}
