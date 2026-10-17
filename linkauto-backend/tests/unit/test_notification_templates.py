import re
from datetime import UTC, datetime
from string import Formatter
from typing import TYPE_CHECKING

import pytest

from app.core.config import Settings
from app.services.auth_service import AuthService
from app.services.booking_notifier import format_lesson_time
from app.services.identity_repository import IdentityRepository
from app.services.notification_service import InMemoryEmailGateway, NotificationService
from app.services.notification_templates import (
    SIGNATURE,
    TEMPLATES,
    EmailTemplateName,
    render_email,
)
from app.services.refresh_token_repository import RefreshTokenRepository

if TYPE_CHECKING:
    from sqlmodel import Session

UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-")


def _fields(text: str) -> set[str]:
    return {name for _, name, _, _ in Formatter().parse(text) if name}


@pytest.mark.parametrize("name", list(EmailTemplateName))
def test_every_template_renders(name: EmailTemplateName) -> None:
    template = TEMPLATES[name]
    values = {field: f"<{field}>" for field in _fields(template.subject) | _fields(template.body)}

    payload = render_email(name, ["to@test.com"], **values)

    assert payload.event == template.event
    assert payload.recipients == ["to@test.com"]
    assert "{" not in payload.subject
    assert payload.body.endswith(SIGNATURE)


def test_missing_value_raises() -> None:
    with pytest.raises(KeyError):
        render_email(EmailTemplateName.BOOKING_CONFIRMED, ["to@test.com"], recipient_name="Ana")


def test_user_text_with_braces_is_inserted_verbatim() -> None:
    payload = render_email(
        EmailTemplateName.BOOKING_MESSAGE,
        ["to@test.com"],
        recipient_name="Ana",
        sender_name="Bia",
        lesson_time="amanhã",
        content="{recipient_name} {0}",
        link="http://app/x",
    )

    assert '"{recipient_name} {0}"' in payload.body


def test_format_lesson_time_matches_the_app() -> None:
    starts = datetime(2026, 10, 17, 9, 0, tzinfo=UTC)
    ends = datetime(2026, 10, 17, 11, 0, tzinfo=UTC)

    assert format_lesson_time(starts, ends) == "sábado, 17/10/2026, das 09:00 às 11:00"


def test_frontend_link_joins_paths() -> None:
    settings = Settings(FRONTEND_URL="https://app.linkauto.com.br/")

    assert settings.frontend_link("/my-lessons") == "https://app.linkauto.com.br/my-lessons"


class TestInstructorRegisteredNotification:
    def _register(
        self, db_session: Session, settings: Settings
    ) -> list[dict[str, str | list[str]]]:
        gateway = InMemoryEmailGateway()
        service = AuthService(
            settings=settings,
            repository=IdentityRepository(db_session),
            refresh_tokens=RefreshTokenRepository(db_session),
            notification_service=NotificationService(gateway),
        )
        service.register(email="new-inst@test.com", password="Pass1234!", roles=["INSTRUTOR"])
        return gateway.sent_messages

    def test_goes_to_the_admin_inbox(self, db_session: Session) -> None:
        settings = Settings(ADMIN_NOTIFICATION_EMAIL="admin@linkauto.test")

        sent = self._register(db_session, settings)

        assert [m["recipients"] for m in sent] == [["admin@linkauto.test"]]
        body = str(sent[0]["body"])
        assert "new-inst@test.com" in body
        assert "/admin/instructors" in body
        assert not UUID.search(body)

    def test_is_skipped_without_an_admin_inbox(self, db_session: Session) -> None:
        settings = Settings(SES_FROM_EMAIL="noreply@linkauto.test")

        # Before #55 this went to SES_FROM_EMAIL, our own sender address
        assert self._register(db_session, settings) == []
