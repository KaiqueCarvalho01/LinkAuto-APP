from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest
from sqlalchemy.exc import StatementError

from app.domain.booking import BookingStatus
from app.models.booking import Booking, BookingSlot, StudentPenalty
from app.models.slot import Slot, SlotStatus

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def test_slot_model_creation(db_session: Session) -> None:
    """Slot model persists with required fields."""
    now = datetime.now(UTC)
    slot = Slot(
        instructor_id="instructor-001",
        starts_at=now,
        ends_at=now + timedelta(hours=1),
        status=SlotStatus.DISPONIVEL,
    )
    db_session.add(slot)
    db_session.flush()

    assert slot.id is not None
    assert slot.status == SlotStatus.DISPONIVEL
    assert slot.ends_at - slot.starts_at == timedelta(hours=1)


def test_booking_model_creation(db_session: Session) -> None:
    """Booking model persists with required fields and default status."""
    booking = Booking(
        student_id="student-001",
        instructor_id="instructor-001",
        status=BookingStatus.PENDENTE,
    )
    db_session.add(booking)
    db_session.flush()

    assert booking.id is not None
    assert booking.status == BookingStatus.PENDENTE
    assert booking.cancelled_by is None


def test_booking_slot_association(db_session: Session) -> None:
    """BookingSlot links a Booking to a Slot."""
    now = datetime.now(UTC)
    slot = Slot(
        instructor_id="instructor-001",
        starts_at=now,
        ends_at=now + timedelta(hours=1),
        status=SlotStatus.RESERVADO,
    )
    booking = Booking(
        student_id="student-001",
        instructor_id="instructor-001",
        status=BookingStatus.PENDENTE,
    )
    db_session.add_all([slot, booking])
    db_session.flush()

    link = BookingSlot(booking_id=booking.id, slot_id=slot.id)
    db_session.add(link)
    db_session.flush()

    assert link.booking_id == booking.id
    assert link.slot_id == slot.id


def test_student_penalty_model(db_session: Session) -> None:
    """StudentPenalty persists with blocking date."""
    penalty = StudentPenalty(
        student_id="student-001",
        blocked_until=datetime.now(UTC) + timedelta(days=7),
        reason="Cancelamento tardio conforme RN04",
    )
    db_session.add(penalty)
    db_session.flush()

    assert penalty.id is not None
    assert penalty.student_id == "student-001"


def test_datetimes_round_trip_as_aware_utc(db_session: Session) -> None:
    """Datetime columns return aware UTC values, even on SQLite (SQLModel UTCDateTime)."""
    start = datetime(2030, 1, 1, 12, tzinfo=UTC)
    slot = Slot(instructor_id="instructor-001", starts_at=start, ends_at=start + timedelta(hours=1))
    db_session.add(slot)
    db_session.flush()
    db_session.expire_all()

    loaded = db_session.get(Slot, slot.id)
    assert loaded is not None
    assert loaded.starts_at == start
    assert loaded.starts_at.tzinfo is not None
    assert loaded.created_at.tzinfo is not None


def test_naive_datetimes_are_rejected(db_session: Session) -> None:
    """Writing a naive datetime fails instead of silently guessing its timezone."""
    naive = datetime(2030, 1, 1, 12)  # noqa: DTZ001 - naive on purpose
    db_session.add(
        Slot(instructor_id="instructor-001", starts_at=naive, ends_at=naive + timedelta(hours=1))
    )

    with pytest.raises(StatementError, match="timezone information"):
        db_session.flush()
