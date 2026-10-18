"""Profile and booking inputs are range- and length-checked (#80)."""

from typing import TYPE_CHECKING

import pytest

from tests.contract.test_us2_booking_contract import (
    _register_login,
    _setup_instructor_with_slots,
)

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session


def _patch_instructor(client: TestClient, headers: dict[str, str], **fields: object) -> int:
    return client.patch(
        "/api/v1/users/me", json={"instructor_profile": fields}, headers=headers
    ).status_code


@pytest.fixture
def instructor(client: TestClient, db_session: Session) -> dict[str, str]:
    _, token = _register_login("INSTRUTOR", "valid-inst@test.com", client, db_session)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(
    "fields",
    [
        {"price_per_hour": -50},
        {"price_per_hour": 100_000},
        {"latitude": 91},
        {"longitude": -181},
        {"action_radius_km": 0},
        {"action_radius_km": -5},
        {"phone": "9" * 31},
        {"city": "x" * 121},
        {"full_name": "x" * 256},
        {"bio": "x" * 2001},
        {"specialties": [f"esp-{n}" for n in range(21)]},
        {"specialties": [""]},
        {"avatar_url": "javascript:alert(1)"},
        {"avatar_url": "http://tracker.example/pixel.png"},
        {"avatar_url": "https://"},
    ],
)
def test_invalid_profile_values_are_rejected(
    client: TestClient, instructor: dict[str, str], fields: dict[str, object]
) -> None:
    assert _patch_instructor(client, instructor, **fields) == 422


def test_valid_edge_values_are_accepted(client: TestClient, instructor: dict[str, str]) -> None:
    status = _patch_instructor(
        client,
        instructor,
        price_per_hour=0,
        latitude=-90,
        longitude=180,
        action_radius_km=200,
        phone="9" * 30,
        avatar_url="https://cdn.linkauto.com.br/a.png",
        specialties=["Baliza", "Rodovia"],
    )

    assert status == 200


@pytest.mark.parametrize(
    "extra",
    [
        {"latitude": 1e9},
        {"longitude": 181},
        {"location_description": "x" * 501},
    ],
)
def test_invalid_booking_values_are_rejected(
    client: TestClient, db_session: Session, extra: dict[str, object]
) -> None:
    inst_id, inst_token = _register_login("INSTRUTOR", "b-inst@test.com", client, db_session)
    _, stu_token = _register_login("ALUNO", "b-stu@test.com", client, db_session)
    slot_ids = _setup_instructor_with_slots(inst_token, client)[:2]

    resp = client.post(
        "/api/v1/bookings",
        json={"instructor_id": inst_id, "slot_ids": slot_ids, **extra},
        headers={"Authorization": f"Bearer {stu_token}"},
    )

    assert resp.status_code == 422


def test_cancellation_reason_is_bounded_and_status_filter_validated(
    client: TestClient, db_session: Session
) -> None:
    _, stu_token = _register_login("ALUNO", "f-stu@test.com", client, db_session)
    headers = {"Authorization": f"Bearer {stu_token}"}

    assert client.get("/api/v1/bookings?status=WHATEVER", headers=headers).status_code == 422
    assert client.get("/api/v1/bookings?status=PENDENTE", headers=headers).status_code == 200
    resp = client.patch("/api/v1/bookings/any/cancel", json={"reason": "x" * 501}, headers=headers)
    assert resp.status_code == 422


def test_custom_validator_errors_come_back_as_422_with_their_message(
    client: TestClient, instructor: dict[str, str]
) -> None:
    """Errors from custom validators carry the exception in ctx; it used to turn into a 500."""
    resp = client.patch(
        "/api/v1/users/me",
        json={"instructor_profile": {"avatar_url": "javascript:alert(1)"}},
        headers=instructor,
    )

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
    issue = resp.json()["meta"]["issues"][0]
    assert issue["ctx"]["error"] == "Must be an https:// URL"
