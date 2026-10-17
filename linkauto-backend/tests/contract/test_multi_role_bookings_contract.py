"""Users with both ALUNO and INSTRUTOR roles use bookings on both sides (#51)."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from app.core.security import hash_password
from app.services.identity_repository import IdentityRepository
from app.services.penalty_service import PenaltyService
from tests.contract.test_us2_booking_contract import (
    _register_login,
    _setup_instructor_with_slots,
)

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session


def _multi_role_login(client: TestClient, db_session: Session) -> tuple[str, dict[str, str]]:
    store = IdentityRepository(db_session)
    user = store.create_user("multi@test.com", hash_password("Pass1234!"), ["ALUNO", "INSTRUTOR"])
    store.update_profile(
        user.id, {"instructor_profile": {"full_name": "Multi", "city": "Mogi", "state": "SP"}}
    )
    store.review_instructor(user.id, status="APROVADO", reviewed_by="admin-id")
    resp = client.post(
        "/api/v1/auth/login", json={"email": "multi@test.com", "password": "Pass1234!"}
    )
    return user.id, {"Authorization": f"Bearer {resp.json()['data']['access_token']}"}


def _book(client: TestClient, headers: dict[str, str], instructor_id: str, slots: list[str]) -> str:
    resp = client.post(
        "/api/v1/bookings",
        json={"instructor_id": instructor_id, "slot_ids": slots[:2]},
        headers=headers,
    )
    assert resp.status_code == 201, resp.json()
    return resp.json()["data"]["id"]


def _listed(client: TestClient, headers: dict[str, str], query: str = "") -> list[str]:
    resp = client.get(f"/api/v1/bookings{query}", headers=headers)
    assert resp.status_code == 200
    return [booking["id"] for booking in resp.json()["data"]]


@dataclass
class Scenario:
    multi_id: str
    multi: dict[str, str]
    as_student: str
    as_instructor: str


@pytest.fixture
def scenario(client: TestClient, db_session: Session) -> Scenario:
    """Seed a multi-role user who booked another instructor and was booked by a student."""
    multi_id, multi = _multi_role_login(client, db_session)
    inst_id, inst_token = _register_login("INSTRUTOR", "other-inst@test.com", client, db_session)
    _, stu_token = _register_login("ALUNO", "other-stu@test.com", client, db_session)
    stu = {"Authorization": f"Bearer {stu_token}"}

    as_student = _book(client, multi, inst_id, _setup_instructor_with_slots(inst_token, client))
    multi_token = multi["Authorization"].removeprefix("Bearer ")
    as_instructor = _book(client, stu, multi_id, _setup_instructor_with_slots(multi_token, client))
    return Scenario(multi_id, multi, as_student, as_instructor)


def test_lists_both_sides_by_default_and_one_side_with_as(
    client: TestClient, scenario: Scenario
) -> None:
    multi = scenario.multi

    assert set(_listed(client, multi)) == {scenario.as_student, scenario.as_instructor}
    assert _listed(client, multi, "?as=student") == [scenario.as_student]
    assert _listed(client, multi, "?as=instructor") == [scenario.as_instructor]
    meta = client.get("/api/v1/bookings", headers=multi).json()["meta"]
    assert meta == {"total": 2, "as": ["student", "instructor"]}


def test_rejects_unknown_side(client: TestClient, scenario: Scenario) -> None:
    resp = client.get("/api/v1/bookings?as=admin", headers=scenario.multi)

    assert resp.status_code == 422


def test_cancels_own_student_booking_as_aluno(
    client: TestClient, db_session: Session, scenario: Scenario
) -> None:
    resp = client.patch(
        f"/api/v1/bookings/{scenario.as_student}/cancel",
        json={"reason": "Imprevisto"},
        headers=scenario.multi,
    )

    assert resp.status_code == 200
    assert resp.json()["data"]["cancelled_by"] == "ALUNO"
    # Slots start in ~4h, so the RN04 late-cancellation penalty applies to the student side
    assert PenaltyService(db_session).is_penalized(scenario.multi_id) is True


def test_cancels_booking_made_with_them_as_instrutor(
    client: TestClient, db_session: Session, scenario: Scenario
) -> None:
    resp = client.patch(
        f"/api/v1/bookings/{scenario.as_instructor}/cancel",
        json={"reason": "Carro na oficina"},
        headers=scenario.multi,
    )

    assert resp.status_code == 200
    assert resp.json()["data"]["cancelled_by"] == "INSTRUTOR"
    assert PenaltyService(db_session).is_penalized(scenario.multi_id) is False


def test_cannot_book_own_slots(client: TestClient, db_session: Session) -> None:
    multi_id, multi = _multi_role_login(client, db_session)
    slots = _setup_instructor_with_slots(multi["Authorization"].removeprefix("Bearer "), client)

    resp = client.post(
        "/api/v1/bookings",
        json={"instructor_id": multi_id, "slot_ids": slots[:2]},
        headers=multi,
    )

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "SLOT_VALIDATION"


def test_single_role_users_keep_their_side(client: TestClient, scenario: Scenario) -> None:
    del scenario
    # The other student only booked, so they see one booking on the student side
    resp = client.post(
        "/api/v1/auth/login", json={"email": "other-stu@test.com", "password": "Pass1234!"}
    )
    headers = {"Authorization": f"Bearer {resp.json()['data']['access_token']}"}

    body = client.get("/api/v1/bookings", headers=headers).json()

    assert body["meta"] == {"total": 1, "as": ["student"]}
