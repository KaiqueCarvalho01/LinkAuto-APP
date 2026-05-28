from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator


class BookingCreateRequest(BaseModel):
    instructor_id: str
    slot_ids: list[str]
    location_description: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    @field_validator("slot_ids")
    @classmethod
    def minimum_2_slots(cls, v: list[str]) -> list[str]:
        if len(v) < 2:
            raise ValueError("Minimum 2 consecutive slots required (RN02)")
        return v


class BookingConfirmRequest(BaseModel):
    pass


class BookingCancelRequest(BaseModel):
    reason: str | None = None


class BookingAdminOverrideRequest(BaseModel):
    status: str
    reason: str

    @field_validator("reason")
    @classmethod
    def reason_min_length(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("Reason must be at least 3 characters")
        return v

    @field_validator("status")
    @classmethod
    def status_must_be_terminal(cls, v: str) -> str:
        if v not in ("REALIZADA", "CANCELADA"):
            raise ValueError("Override status must be REALIZADA or CANCELADA")
        return v


class BookingResource(BaseModel):
    id: str
    student_id: str
    instructor_id: str
    status: str
    location_description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    created_at: datetime
    confirmed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancelled_by: str | None = None
    cancellation_reason: str | None = None

    model_config = {"from_attributes": True}
