"""Request and response schemas for bookings."""

from __future__ import annotations

from pydantic import BaseModel, field_validator

from app.domain.booking import MIN_SLOTS_PER_BOOKING
from app.schemas.datetime import UtcDateTime
from app.schemas.slot import SlotResource

MIN_OVERRIDE_REASON_LENGTH = 3


class BookingCreateRequest(BaseModel):
    """Payload for a student to request a booking of an instructor's slots (at least 2)."""

    instructor_id: str
    slot_ids: list[str]
    location_description: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    @field_validator("slot_ids")
    @classmethod
    def minimum_2_slots(cls, v: list[str]) -> list[str]:
        """Reject requests with fewer than MIN_SLOTS_PER_BOOKING slot IDs (rule RN02)."""
        if len(v) < MIN_SLOTS_PER_BOOKING:
            msg = "Minimum 2 consecutive slots required (RN02)"
            raise ValueError(msg)
        return v


class BookingConfirmRequest(BaseModel):
    """Empty payload for an instructor to confirm a pending booking."""


class BookingCancelRequest(BaseModel):
    """Payload to cancel a booking, with an optional reason."""

    reason: str | None = None


class BookingAdminOverrideRequest(BaseModel):
    """Payload for an admin to force a booking into REALIZADA or CANCELADA with a reason."""

    status: str
    reason: str

    @field_validator("reason")
    @classmethod
    def reason_min_length(cls, v: str) -> str:
        """Require a reason of at least MIN_OVERRIDE_REASON_LENGTH non-blank characters."""
        if len(v.strip()) < MIN_OVERRIDE_REASON_LENGTH:
            msg = f"Reason must be at least {MIN_OVERRIDE_REASON_LENGTH} characters"
            raise ValueError(msg)
        return v

    @field_validator("status")
    @classmethod
    def status_must_be_terminal(cls, v: str) -> str:
        """Allow only the terminal statuses REALIZADA and CANCELADA."""
        if v not in ("REALIZADA", "CANCELADA"):
            msg = "Override status must be REALIZADA or CANCELADA"
            raise ValueError(msg)
        return v


class BookingSlotResource(BaseModel):
    """Slot reserved by a booking, including the slot details."""

    id: str
    booking_id: str
    slot_id: str
    slot: SlotResource

    model_config = {"from_attributes": True}


class BookingResource(BaseModel):
    """Booking between a student and an instructor, with its status and reserved slots.

    Status is PENDENTE, CONFIRMADA, REALIZADA or CANCELADA; timestamps are UTC.
    """

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
