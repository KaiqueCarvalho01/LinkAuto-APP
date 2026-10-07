"""Request and response schemas for instructor availability slots."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, field_validator, model_validator

from app.schemas.datetime import UtcDateTime


class SlotCreateRequest(BaseModel):
    """Payload for an instructor to open a slot: exactly 1 hour, starting in the future."""

    starts_at: UtcDateTime
    ends_at: UtcDateTime

    @field_validator("starts_at")
    @classmethod
    def starts_at_must_be_future(cls, v: datetime) -> datetime:
        """Reject start times that are not in the future."""
        if v <= datetime.now(UTC):
            msg = "starts_at must be in the future"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def duration_must_be_1h(self) -> SlotCreateRequest:
        """Require ``ends_at`` to be exactly one hour after ``starts_at``."""
        expected = timedelta(hours=1)
        actual = self.ends_at - self.starts_at
        if actual != expected:
            msg = f"Slot duration must be exactly 1 hour, got {actual}"
            raise ValueError(msg)
        return self


class SlotResource(BaseModel):
    """Instructor availability slot with UTC times and status (DISPONIVEL, RESERVADO, BLOQUEADO)."""

    id: str
    instructor_id: str
    starts_at: UtcDateTime
    ends_at: UtcDateTime
    status: str

    model_config = {"from_attributes": True}
