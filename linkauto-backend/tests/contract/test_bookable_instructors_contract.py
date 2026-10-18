"""Only DETRAN-approved, active instructors can be booked or have public slots (#71, RN01)."""

from typing import TYPE_CHECKING

import pytest

from app.models import InstructorProfile, User
from app.models.user import DetranStatus
from tests.contract.test_us2_booking_contract import (
    _register_login,
    _setup_instructor_with_slots,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from fastapi.testclient import TestClient
    from sqlmodel import Session


def _pending(profile: InstructorProfile, _user: User) -> None:
    profile.detran_status = DetranStatus.PENDENTE


def _rejected(profile: InstructorProfile, _user: User) -> None:
    profile.detran_status = DetranStatus.REJEITADO


def _paused(profile: InstructorProfile, _user: User) -> None:
    profile.is_active = False


def _deactivated(_profile: InstructorProfile, user: User) -> None:
    user.is_active = False


@pytest.mark.parametrize("make_unbookable", [_pending, _rejected, _paused, _deactivated])
def test_unbookable_instructors_cannot_be_booked_or_listed(
    client: TestClient,
    db_session: Session,
    make_unbookable: Callable[[InstructorProfile, User], None],
) -> None:
    inst_id, inst_token = _register_login("INSTRUTOR", "unbookable@test.com", client, db_session)
    _, stu_token = _register_login("ALUNO", "unbookable-stu@test.com", client, db_session)
    slot_ids = _setup_instructor_with_slots(inst_token, client)
    profile = db_session.get(InstructorProfile, inst_id)
    user = db_session.get(User, inst_id)
    assert profile is not None
    assert user is not None
    make_unbookable(profile, user)
    db_session.commit()

    booking = client.post(
        "/api/v1/bookings",
        json={"instructor_id": inst_id, "slot_ids": slot_ids[:2]},
        headers={"Authorization": f"Bearer {stu_token}"},
    )
    public_slots = client.get(f"/api/v1/instructors/{inst_id}/slots")

    assert booking.status_code == 404
    assert booking.json()["error"]["code"] == "INSTRUCTOR_NOT_FOUND"
    assert public_slots.status_code == 404


def test_approved_instructors_slots_are_public_by_id_and_slug(
    client: TestClient, db_session: Session
) -> None:
    inst_id, inst_token = _register_login("INSTRUTOR", "approved@test.com", client, db_session)
    _setup_instructor_with_slots(inst_token, client)
    profile = db_session.get(InstructorProfile, inst_id)
    assert profile is not None
    profile.slug = "ana-mogi"
    db_session.commit()

    for ref in (inst_id, "ana-mogi"):
        resp = client.get(f"/api/v1/instructors/{ref}/slots")
        assert resp.status_code == 200
        assert resp.json()["meta"]["total"] == 3


def test_pending_instructors_can_prepare_their_agenda(
    client: TestClient, db_session: Session
) -> None:
    inst_id, inst_token = _register_login("INSTRUTOR", "pending@test.com", client, db_session)
    profile = db_session.get(InstructorProfile, inst_id)
    assert profile is not None
    profile.detran_status = DetranStatus.PENDENTE
    db_session.commit()

    _setup_instructor_with_slots(inst_token, client)
    mine = client.get(
        "/api/v1/instructors/me/slots", headers={"Authorization": f"Bearer {inst_token}"}
    )

    assert mine.json()["meta"]["total"] == 3
    assert client.get(f"/api/v1/instructors/{inst_id}/slots").status_code == 404


def test_unknown_instructor_is_not_found(client: TestClient, db_session: Session) -> None:
    _, stu_token = _register_login("ALUNO", "nobody-stu@test.com", client, db_session)

    resp = client.post(
        "/api/v1/bookings",
        json={"instructor_id": "does-not-exist", "slot_ids": ["a", "b"]},
        headers={"Authorization": f"Bearer {stu_token}"},
    )

    assert resp.status_code == 404
