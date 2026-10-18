"""Slots in the past can't be booked, listed publicly, or confirmed (#70)."""

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlmodel import col, select

from app.models import Slot
from tests.contract.test_us2_booking_contract import (
    _register_login,
    _setup_instructor_with_slots,
)

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session


def _move_to_the_past(db_session: Session, slot_ids: list[str]) -> None:
    slots = db_session.exec(
        select(Slot).where(col(Slot.id).in_(slot_ids)).order_by(col(Slot.starts_at))
    ).all()
    start = datetime.now(UTC) - timedelta(days=2)
    for index, slot in enumerate(slots):
        slot.starts_at = start + timedelta(hours=index)
        slot.ends_at = start + timedelta(hours=index + 1)
    db_session.commit()


def test_past_slots_cannot_be_booked(client: TestClient, db_session: Session) -> None:
    inst_id, inst_token = _register_login("INSTRUTOR", "past-inst@test.com", client, db_session)
    _, stu_token = _register_login("ALUNO", "past-stu@test.com", client, db_session)
    slot_ids = _setup_instructor_with_slots(inst_token, client)[:2]
    _move_to_the_past(db_session, slot_ids)

    resp = client.post(
        "/api/v1/bookings",
        json={"instructor_id": inst_id, "slot_ids": slot_ids},
        headers={"Authorization": f"Bearer {stu_token}"},
    )

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "SLOT_VALIDATION"
    assert "future" in resp.json()["error"]["message"]


def test_past_slots_are_not_listed_publicly(client: TestClient, db_session: Session) -> None:
    inst_id, inst_token = _register_login("INSTRUTOR", "list-inst@test.com", client, db_session)
    slot_ids = _setup_instructor_with_slots(inst_token, client)
    _move_to_the_past(db_session, slot_ids[:2])

    public = client.get(f"/api/v1/instructors/{inst_id}/slots").json()
    mine = client.get(
        "/api/v1/instructors/me/slots", headers={"Authorization": f"Bearer {inst_token}"}
    ).json()

    assert [slot["id"] for slot in public["data"]] == [slot_ids[2]]
    # The instructor still sees their whole history
    assert mine["meta"]["total"] == 3


def test_a_started_lesson_cannot_be_confirmed(client: TestClient, db_session: Session) -> None:
    inst_id, inst_token = _register_login("INSTRUTOR", "late-inst@test.com", client, db_session)
    _, stu_token = _register_login("ALUNO", "late-stu@test.com", client, db_session)
    slot_ids = _setup_instructor_with_slots(inst_token, client)[:2]
    booking_id = client.post(
        "/api/v1/bookings",
        json={"instructor_id": inst_id, "slot_ids": slot_ids},
        headers={"Authorization": f"Bearer {stu_token}"},
    ).json()["data"]["id"]
    _move_to_the_past(db_session, slot_ids)

    resp = client.patch(
        f"/api/v1/bookings/{booking_id}/confirm",
        headers={"Authorization": f"Bearer {inst_token}"},
    )

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "INVALID_TRANSITION"
    status = client.get(
        f"/api/v1/bookings/{booking_id}", headers={"Authorization": f"Bearer {inst_token}"}
    ).json()["data"]["status"]
    assert status == "PENDENTE"
