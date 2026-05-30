from datetime import datetime, timedelta, timezone

from app.models.slot import Slot, SlotStatus
from app.models.booking import Booking, BookingSlot, StudentPenalty
from app.domain.booking import BookingStatus


def test_slot_model_creation(db_session):
    """Slot model persists with required fields."""
    now = datetime.now(timezone.utc)
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


def test_booking_model_creation(db_session):
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


def test_booking_slot_association(db_session):
    """BookingSlot links a Booking to a Slot."""
    now = datetime.now(timezone.utc)
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


def test_student_penalty_model(db_session):
    """StudentPenalty persists with blocking date."""
    penalty = StudentPenalty(
        student_id="student-001",
        blocked_until=datetime.now(timezone.utc) + timedelta(days=7),
        reason="Cancelamento tardio conforme RN04",
    )
    db_session.add(penalty)
    db_session.flush()

    assert penalty.id is not None
    assert penalty.student_id == "student-001"
