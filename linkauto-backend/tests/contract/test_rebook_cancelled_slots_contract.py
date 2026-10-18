"""Slots freed by a cancellation can be booked again, and only once at a time (#69)."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, override

import pytest
from sqlmodel import col, select

from app.models import Booking, BookingSlot, Slot
from app.models.slot import SlotStatus
from app.services.booking_service import BookingService, SlotValidationError
from tests.contract.test_us2_booking_contract import (
    _register_login,
    _setup_instructor_with_slots,
)
from tests.factories import admin_headers

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session


@dataclass
class Booked:
    inst_id: str
    inst_token: str
    stu_token: str
    other_token: str
    booking_id: str
    slot_ids: list[str]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _book(client: TestClient, token: str, instructor_id: str, slot_ids: list[str]) -> int:
    return client.post(
        "/api/v1/bookings",
        json={"instructor_id": instructor_id, "slot_ids": slot_ids},
        headers=_auth(token),
    ).status_code


@pytest.fixture
def booked(client: TestClient, db_session: Session) -> Booked:
    inst_id, inst_token = _register_login("INSTRUTOR", "rebook-inst@test.com", client, db_session)
    _, stu_token = _register_login("ALUNO", "rebook-stu@test.com", client, db_session)
    _, other_token = _register_login("ALUNO", "rebook-other@test.com", client, db_session)
    slot_ids = _setup_instructor_with_slots(inst_token, client)[:2]
    resp = client.post(
        "/api/v1/bookings",
        json={"instructor_id": inst_id, "slot_ids": slot_ids},
        headers=_auth(stu_token),
    )
    assert resp.status_code == 201
    return Booked(
        inst_id=inst_id,
        inst_token=inst_token,
        stu_token=stu_token,
        other_token=other_token,
        booking_id=resp.json()["data"]["id"],
        slot_ids=slot_ids,
    )


@pytest.mark.parametrize("who", ["student", "instructor", "admin"])
def test_slots_can_be_booked_again_after_a_cancellation(
    client: TestClient, db_session: Session, booked: Booked, who: str
) -> None:
    booking_id = booked.booking_id
    if who == "admin":
        resp = client.patch(
            f"/api/v1/admin/bookings/{booking_id}/override-status",
            json={"status": "CANCELADA", "reason": "Fraude"},
            headers=admin_headers(db_session),
        )
    else:
        token = booked.stu_token if who == "student" else booked.inst_token
        resp = client.patch(f"/api/v1/bookings/{booking_id}/cancel", json={}, headers=_auth(token))
    assert resp.status_code == 200

    assert _book(client, booked.other_token, booked.inst_id, booked.slot_ids) == 201

    # The cancelled booking keeps its slots as history
    history = client.get(f"/api/v1/bookings/{booking_id}", headers=_auth(booked.inst_token))
    assert len(history.json()["data"]["slots"]) == 2


def test_system_timeout_frees_the_slots_for_rebooking(
    client: TestClient, db_session: Session, booked: Booked
) -> None:
    booking = db_session.get(Booking, booked.booking_id)
    assert booking is not None
    booking.created_at = datetime.now(UTC) - timedelta(days=2)
    db_session.commit()

    resp = client.post("/api/v1/jobs/booking-timeout", headers=admin_headers(db_session))

    assert resp.json()["data"]["processed"] == 1
    assert _book(client, booked.other_token, booked.inst_id, booked.slot_ids) == 201


def test_held_slots_still_cannot_be_booked_twice(client: TestClient, booked: Booked) -> None:
    assert _book(client, booked.other_token, booked.inst_id, booked.slot_ids) == 422


def test_a_stale_read_cannot_double_book(db_session: Session, booked: Booked) -> None:
    """Two requests that both saw the slots available: the second one must lose."""
    slots = list(db_session.exec(select(Slot).where(col(Slot.id).in_(booked.slot_ids))).all())
    student_id = db_session.exec(
        select(Booking.student_id).where(col(Booking.id) == booked.booking_id)
    ).one()

    class StaleReadService(BookingService):
        """Validation ran before the first booking reserved the slots."""

        @override
        def _get_bookable_slots(self, slot_ids: list[str], instructor_id: str) -> list[Slot]:
            del slot_ids, instructor_id
            return slots

    with pytest.raises(SlotValidationError, match="just booked"):
        StaleReadService(db_session).create_booking(student_id, booked.inst_id, booked.slot_ids)
    links = db_session.exec(select(BookingSlot).where(col(BookingSlot.slot_id) == slots[0].id))
    assert [link.booking_id for link in links] == [booked.booking_id]


def test_removing_a_freed_slot_keeps_the_booking_history(
    client: TestClient, db_session: Session, booked: Booked
) -> None:
    inst = _auth(booked.inst_token)
    client.patch(f"/api/v1/bookings/{booked.booking_id}/cancel", json={}, headers=inst)
    slot_id = booked.slot_ids[0]

    resp = client.delete(f"/api/v1/instructors/me/slots/{slot_id}", headers=inst)

    assert resp.status_code == 200
    db_session.expire_all()
    slot = db_session.get(Slot, slot_id)
    assert slot is not None
    assert slot.status == SlotStatus.BLOQUEADO.value
    mine = client.get("/api/v1/instructors/me/slots", headers=inst).json()["data"]
    assert slot_id not in [s["id"] for s in mine]
    history = client.get(f"/api/v1/bookings/{booked.booking_id}", headers=inst)
    assert len(history.json()["data"]["slots"]) == 2
    # The hour can be opened again
    reopened = client.post(
        "/api/v1/instructors/me/slots",
        json={"starts_at": slot.starts_at.isoformat(), "ends_at": slot.ends_at.isoformat()},
        headers=inst,
    )
    assert reopened.status_code == 201
