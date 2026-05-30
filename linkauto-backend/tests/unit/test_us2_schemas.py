from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.schemas.slot import SlotCreateRequest, SlotResource
from app.schemas.booking import BookingCreateRequest, BookingResource


class TestSlotSchemas:
    def test_slot_create_valid(self):
        now = datetime.now(timezone.utc)
        req = SlotCreateRequest(
            starts_at=now + timedelta(hours=1),
            ends_at=now + timedelta(hours=2),
        )
        assert req.starts_at is not None

    def test_slot_create_rejects_past_starts_at(self):
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        with pytest.raises(ValidationError):
            SlotCreateRequest(
                starts_at=past,
                ends_at=past + timedelta(hours=1),
            )

    def test_slot_create_rejects_non_1h_duration(self):
        now = datetime.now(timezone.utc) + timedelta(hours=1)
        with pytest.raises(ValidationError):
            SlotCreateRequest(
                starts_at=now,
                ends_at=now + timedelta(hours=2),
            )

    def test_slot_resource_serializes(self):
        now = datetime.now(timezone.utc)
        res = SlotResource(
            id="slot-001",
            instructor_id="inst-001",
            starts_at=now,
            ends_at=now + timedelta(hours=1),
            status="DISPONIVEL",
        )
        assert res.id == "slot-001"


class TestBookingSchemas:
    def test_booking_create_valid(self):
        req = BookingCreateRequest(
            instructor_id="inst-001",
            slot_ids=["slot-001", "slot-002"],
        )
        assert len(req.slot_ids) == 2

    def test_booking_create_rejects_less_than_2_slots(self):
        with pytest.raises(ValidationError):
            BookingCreateRequest(
                instructor_id="inst-001",
                slot_ids=["slot-001"],
            )

    def test_booking_resource_serializes(self):
        now = datetime.now(timezone.utc)
        res = BookingResource(
            id="book-001",
            student_id="stu-001",
            instructor_id="inst-001",
            status="PENDENTE",
            created_at=now,
        )
        assert res.status == "PENDENTE"
