"""Booking messages are bounded, rate-limited and closed on cancelled bookings (#77)."""

from typing import TYPE_CHECKING

import pytest

from tests.contract.test_us2_booking_contract import (
    _register_login,
    _setup_instructor_with_slots,
)

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session

    from app.services.notification_service import InMemoryEmailGateway


@pytest.fixture
def chat(client: TestClient, db_session: Session) -> tuple[str, dict[str, str]]:
    """Create a pending booking; return its messages URL and the student's headers."""
    inst_id, inst_token = _register_login("INSTRUTOR", "chat-inst@test.com", client, db_session)
    _, stu_token = _register_login("ALUNO", "chat-stu@test.com", client, db_session)
    headers = {"Authorization": f"Bearer {stu_token}"}
    booking_id = client.post(
        "/api/v1/bookings",
        json={
            "instructor_id": inst_id,
            "slot_ids": _setup_instructor_with_slots(inst_token, client)[:2],
        },
        headers=headers,
    ).json()["data"]["id"]
    return f"/api/v1/bookings/{booking_id}/messages", headers


def _send(client: TestClient, chat: tuple[str, dict[str, str]], content: str) -> int:
    url, headers = chat
    return client.post(url, json={"content": content}, headers=headers).status_code


def test_messages_are_at_most_2000_characters(
    client: TestClient, chat: tuple[str, dict[str, str]]
) -> None:
    assert _send(client, chat, "x" * 2000) == 201
    assert _send(client, chat, "x" * 2001) == 422


def test_each_user_can_send_20_messages_per_minute(
    client: TestClient, chat: tuple[str, dict[str, str]], email_outbox: InMemoryEmailGateway
) -> None:
    statuses = [_send(client, chat, f"oi {n}") for n in range(21)]

    assert statuses[:20] == [201] * 20
    assert statuses[20] == 429
    assert len(email_outbox.sent_messages) == 20


def test_cancelled_bookings_do_not_take_messages(
    client: TestClient, chat: tuple[str, dict[str, str]], email_outbox: InMemoryEmailGateway
) -> None:
    url, headers = chat
    client.patch(url.removesuffix("/messages") + "/cancel", json={}, headers=headers)
    email_outbox.sent_messages.clear()

    resp = client.post(url, json={"content": "ainda aí?"}, headers=headers)

    assert resp.status_code == 409
    assert email_outbox.sent_messages == []
    # The history stays readable
    assert client.get(url, headers=headers).status_code == 200


def test_the_email_only_previews_long_messages(
    client: TestClient, chat: tuple[str, dict[str, str]], email_outbox: InMemoryEmailGateway
) -> None:
    _send(client, chat, "a" * 280 + "b" * 500)

    body = str(email_outbox.sent_messages[-1]["body"])
    assert "a" * 280 + "b" * 20 + "…" in body
    assert "b" * 21 not in body
