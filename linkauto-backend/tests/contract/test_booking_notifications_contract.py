"""The booking routes send their e-mails through the notification service (#50)."""

from typing import TYPE_CHECKING, cast

from app.models import InstructorProfile
from app.services.dependencies import get_notification_service
from app.services.identity_repository import IdentityRepository
from app.services.notification_service import DisabledEmailGateway, NotificationService
from tests.contract.test_us2_booking_contract import (
    _register_login,
    _setup_instructor_with_slots,
)

if TYPE_CHECKING:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from sqlmodel import Session

    from app.services.notification_service import InMemoryEmailGateway


def _recipients(outbox: InMemoryEmailGateway) -> list[list[str] | str]:
    return [message["recipients"] for message in outbox.sent_messages]


def _book(client: TestClient, token: str, instructor_ref: str, slot_ids: list[str]) -> str:
    resp = client.post(
        "/api/v1/bookings",
        json={"instructor_id": instructor_ref, "slot_ids": slot_ids[:2]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


def test_booking_by_slug_emails_the_instructor(
    client: TestClient, db_session: Session, email_outbox: InMemoryEmailGateway
) -> None:
    inst_id, inst_token = _register_login("INSTRUTOR", "slug-inst@test.com", client, db_session)
    _, stu_token = _register_login("ALUNO", "slug-stu@test.com", client, db_session)
    profile = db_session.get(InstructorProfile, inst_id)
    assert profile is not None
    slug = IdentityRepository(db_session).ensure_instructor_slug(profile)
    db_session.commit()
    slot_ids = _setup_instructor_with_slots(inst_token, client)

    _book(client, stu_token, slug, slot_ids)

    assert _recipients(email_outbox) == [["slug-inst@test.com"]]


def test_confirm_and_cancel_email_the_other_party(
    client: TestClient, db_session: Session, email_outbox: InMemoryEmailGateway
) -> None:
    inst_id, inst_token = _register_login("INSTRUTOR", "flow-inst@test.com", client, db_session)
    _, stu_token = _register_login("ALUNO", "flow-stu@test.com", client, db_session)
    slot_ids = _setup_instructor_with_slots(inst_token, client)
    booking_id = _book(client, stu_token, inst_id, slot_ids)
    email_outbox.sent_messages.clear()

    resp = client.patch(
        f"/api/v1/bookings/{booking_id}/confirm",
        headers={"Authorization": f"Bearer {inst_token}"},
    )
    assert resp.status_code == 200
    assert _recipients(email_outbox) == [["flow-stu@test.com"]]
    email_outbox.sent_messages.clear()

    resp = client.patch(
        f"/api/v1/bookings/{booking_id}/cancel",
        json={"reason": "Imprevisto"},
        headers={"Authorization": f"Bearer {stu_token}"},
    )
    assert resp.status_code == 200
    assert _recipients(email_outbox) == [["flow-inst@test.com"]]


def test_bookings_work_with_email_disabled(client: TestClient, db_session: Session) -> None:
    """With no e-mail provider configured the routes still succeed."""
    app = cast("FastAPI", client.app)
    app.dependency_overrides[get_notification_service] = lambda: NotificationService(
        DisabledEmailGateway()
    )
    inst_id, inst_token = _register_login("INSTRUTOR", "off-inst@test.com", client, db_session)
    _, stu_token = _register_login("ALUNO", "off-stu@test.com", client, db_session)
    slot_ids = _setup_instructor_with_slots(inst_token, client)
    booking_id = _book(client, stu_token, inst_id, slot_ids)

    resp = client.patch(
        f"/api/v1/bookings/{booking_id}/confirm",
        headers={"Authorization": f"Bearer {inst_token}"},
    )
    assert resp.status_code == 200
