from __future__ import annotations


from pydantic import BaseModel, field_validator

from app.schemas.datetime import UtcDateTime
from app.schemas.slot import SlotResource


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


class BookingSlotResource(BaseModel):
    id: str
    booking_id: str
    slot_id: str
    slot: SlotResource

    model_config = {"from_attributes": True}


class BookingResource(BaseModel):
    id: str
    student_id: str
    instructor_id: str
    status: str
    location_description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    created_at: UtcDateTime
    confirmed_at: UtcDateTime | None = None
    cancelled_at: UtcDateTime | None = None
    cancelled_by: str | None = None
    cancellation_reason: str | None = None
    slots: list[BookingSlotResource] = []

    model_config = {"from_attributes": True}
