"""Concurrent status changes don't overwrite each other (#73).

Each test loads a booking, then changes its status behind the session's back (as another
request or the timeout job would), and runs the competing change with the stale copy.
"""

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import text

from app.domain.booking import BookingStatus, BookingTransitionError
from app.models.slot import SlotStatus
from app.services.admin_booking_service import AdminBookingService
from app.services.booking_service import BookingService
from tests.factories import seed_admin
from tests.unit.test_booking_service import _create_consecutive_slots, _seed_users

if TYPE_CHECKING:
    from sqlmodel import Session

    from app.models import Booking


def _booking(db_session: Session) -> Booking:
    _seed_users(db_session)
    slots = _create_consecutive_slots(db_session, "inst-001", base_offset_hours=48)
    return BookingService(db_session).create_booking("stu-001", "inst-001", [s.id for s in slots])


def _changed_elsewhere(db_session: Session, booking: Booking, status: str) -> None:
    db_session.exec(  # ty: ignore[no-matching-overload]
        text("UPDATE bookings SET status = :status WHERE id = :id"),
        params={"status": status, "id": booking.id},
    )


def _stored_status(db_session: Session, booking: Booking) -> str:
    db_session.refresh(booking)
    return booking.status


def test_confirm_does_not_overwrite_a_concurrent_cancellation(db_session: Session) -> None:
    booking = _booking(db_session)
    _changed_elsewhere(db_session, booking, BookingStatus.CANCELADA.value)

    with pytest.raises(BookingTransitionError, match="changed in the meantime"):
        BookingService(db_session).confirm_booking(booking.id, "inst-001")

    assert _stored_status(db_session, booking) == BookingStatus.CANCELADA.value


def test_cancel_does_not_overwrite_a_concurrent_confirmation(db_session: Session) -> None:
    booking = _booking(db_session)
    _changed_elsewhere(db_session, booking, BookingStatus.CONFIRMADA.value)

    with pytest.raises(BookingTransitionError, match="changed in the meantime"):
        BookingService(db_session).cancel_booking(booking.id, "stu-001", "Imprevisto")

    assert _stored_status(db_session, booking) == BookingStatus.CONFIRMADA.value
    # The confirmed lesson keeps its slots
    for link in booking.slots:
        db_session.refresh(link.slot)
        assert link.slot.status == SlotStatus.RESERVADO.value


def test_admin_override_does_not_overwrite_a_concurrent_change(db_session: Session) -> None:
    booking = _booking(db_session)
    BookingService(db_session).confirm_booking(booking.id, "inst-001")
    seed_admin(db_session)
    # Read as CONFIRMADA (a valid start for the override), then cancelled elsewhere
    _changed_elsewhere(db_session, booking, BookingStatus.CANCELADA.value)

    with pytest.raises(BookingTransitionError, match="changed in the meantime"):
        AdminBookingService(db_session).override_status(
            booking.id, "REALIZADA", "Aula dada", admin_id="admin-1"
        )

    assert _stored_status(db_session, booking) == BookingStatus.CANCELADA.value
