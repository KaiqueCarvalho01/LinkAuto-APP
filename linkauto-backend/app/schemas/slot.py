from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, field_validator, model_validator

from app.schemas.datetime import UtcDateTime


class SlotCreateRequest(BaseModel):
    starts_at: UtcDateTime
    ends_at: UtcDateTime

    @field_validator("starts_at")
    @classmethod
    def starts_at_must_be_future(cls, v: datetime) -> datetime:
        if v <= datetime.now(timezone.utc):
            raise ValueError("starts_at must be in the future")
        return v

    @model_validator(mode="after")
    def duration_must_be_1h(self) -> SlotCreateRequest:
        expected = timedelta(hours=1)
        actual = self.ends_at - self.starts_at
        if actual != expected:
            raise ValueError(f"Slot duration must be exactly 1 hour, got {actual}")
        return self


class SlotResource(BaseModel):
    id: str
    instructor_id: str
    starts_at: UtcDateTime
    ends_at: UtcDateTime
    status: str

    model_config = {"from_attributes": True}
