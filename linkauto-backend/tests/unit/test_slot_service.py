from datetime import datetime, timedelta, timezone

import pytest

from app.models.slot import Slot, SlotStatus
from app.models.user import InstructorProfile, User, UserRole, DetranStatus
from app.services.slot_service import SlotService, SlotOverlapError


def _seed_instructor(db_session, instructor_id="inst-001"):
    user = User(
        id=instructor_id,
        email=f"{instructor_id}@test.com",
        password_hash="fakehash",
        roles=[UserRole.INSTRUTOR.value],
    )
    profile = InstructorProfile(
        user_id=instructor_id,
        full_name="Test Instructor",
        phone="11999999999",
        city="Mogi Mirim",
        state="SP",
        detran_status=DetranStatus.APROVADO,
    )
    db_session.add_all([user, profile])
    db_session.flush()
    return instructor_id


class TestSlotServiceCreate:
    def test_creates_slot_successfully(self, db_session):
        instructor_id = _seed_instructor(db_session)
        service = SlotService(db_session)
        now = datetime.now(timezone.utc) + timedelta(hours=1)

        slot = service.create_slot(
            instructor_id=instructor_id,
            starts_at=now,
            ends_at=now + timedelta(hours=1),
        )

        assert slot.id is not None
        assert slot.status == SlotStatus.DISPONIVEL.value
        assert slot.instructor_id == instructor_id

    def test_rejects_overlapping_slot(self, db_session):
        instructor_id = _seed_instructor(db_session)
        service = SlotService(db_session)
        now = datetime.now(timezone.utc) + timedelta(hours=2)

        service.create_slot(instructor_id, now, now + timedelta(hours=1))

        with pytest.raises(SlotOverlapError):
            service.create_slot(instructor_id, now, now + timedelta(hours=1))


class TestSlotServiceList:
    def test_lists_slots_for_instructor(self, db_session):
        instructor_id = _seed_instructor(db_session)
        service = SlotService(db_session)
        now = datetime.now(timezone.utc) + timedelta(hours=1)

        service.create_slot(instructor_id, now, now + timedelta(hours=1))
        service.create_slot(instructor_id, now + timedelta(hours=1), now + timedelta(hours=2))

        slots = service.list_slots(instructor_id)
        assert len(slots) == 2


class TestSlotServiceDelete:
    def test_deletes_available_slot(self, db_session):
        instructor_id = _seed_instructor(db_session)
        service = SlotService(db_session)
        now = datetime.now(timezone.utc) + timedelta(hours=1)

        slot = service.create_slot(instructor_id, now, now + timedelta(hours=1))
        service.delete_slot(instructor_id, slot.id)

        slots = service.list_slots(instructor_id)
        assert len(slots) == 0

    def test_cannot_delete_reserved_slot(self, db_session):
        instructor_id = _seed_instructor(db_session)
        service = SlotService(db_session)
        now = datetime.now(timezone.utc) + timedelta(hours=1)

        slot = service.create_slot(instructor_id, now, now + timedelta(hours=1))
        slot.status = SlotStatus.RESERVADO.value
        db_session.flush()

        with pytest.raises(ValueError, match="reserved"):
            service.delete_slot(instructor_id, slot.id)
