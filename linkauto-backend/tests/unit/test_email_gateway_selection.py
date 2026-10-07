"""The e-mail gateway is chosen from settings (#24)."""

import logging
import threading
from typing import TYPE_CHECKING

from app.core.config import Settings
from app.services.notification_service import (
    BackgroundEmailGateway,
    DisabledEmailGateway,
    InMemoryEmailGateway,
    NotificationEvent,
    NotificationPayload,
    NotificationService,
    SESEmailGateway,
    build_email_gateway,
)

if TYPE_CHECKING:
    import pytest


def _production(ses_from_email: str | None = None) -> Settings:
    return Settings(
        APP_ENV="production",
        JWT_SECRET="s3cret",
        RESET_SQLITE_ON_STARTUP=False,
        SES_FROM_EMAIL=ses_from_email,
    )


def test_development_without_ses_uses_in_memory_gateway() -> None:
    assert isinstance(build_email_gateway(Settings(APP_ENV="development")), InMemoryEmailGateway)


def test_configured_ses_sender_selects_ses_in_the_background() -> None:
    gateway = build_email_gateway(
        Settings(APP_ENV="staging", SES_FROM_EMAIL="no-reply@linkauto.com.br")
    )

    assert isinstance(gateway, BackgroundEmailGateway)
    assert isinstance(gateway.inner, SESEmailGateway)


def test_production_starts_without_any_email_provider() -> None:
    """E-mail is optional: there is no provider yet, so notifications are simply skipped."""
    gateway = build_email_gateway(_production())

    assert isinstance(gateway, DisabledEmailGateway)


def test_non_development_without_ses_disables_email() -> None:
    assert isinstance(build_email_gateway(Settings(APP_ENV="staging")), DisabledEmailGateway)


def test_production_with_ses_sender_uses_ses() -> None:
    settings = _production("no-reply@linkauto.com.br")

    assert isinstance(build_email_gateway(settings), BackgroundEmailGateway)


def test_email_backend_can_disable_email() -> None:
    settings = Settings(
        APP_ENV="staging", SES_FROM_EMAIL="no-reply@linkauto.com.br", EMAIL_BACKEND="disabled"
    )

    assert isinstance(build_email_gateway(settings), DisabledEmailGateway)


def test_disabled_gateway_drops_notifications_without_failing() -> None:
    service = NotificationService(DisabledEmailGateway())

    result = service.dispatch(
        NotificationPayload(
            event=NotificationEvent.BOOKING_CONFIRMED,
            subject="s",
            body="b",
            recipients=["a@x.com"],
        )
    )

    assert result.delivered is False
    assert result.provider_message_id is None


def test_email_backend_can_force_the_in_memory_gateway() -> None:
    settings = Settings(
        APP_ENV="staging", SES_FROM_EMAIL="no-reply@linkauto.com.br", EMAIL_BACKEND="memory"
    )

    assert isinstance(build_email_gateway(settings), InMemoryEmailGateway)


class _BlockingGateway:
    def __init__(self) -> None:
        self.release = threading.Event()
        self.sent = threading.Event()

    def send(self, subject: str, body: str, recipients: list[str]) -> str:  # noqa: ARG002
        self.release.wait(timeout=5)
        self.sent.set()
        return "msg-1"


def test_background_gateway_does_not_block_the_caller() -> None:
    inner = _BlockingGateway()
    gateway = BackgroundEmailGateway(inner)

    message_id = gateway.send("s", "b", ["a@x.com"])

    assert message_id.startswith("queued-")
    assert not inner.sent.is_set()
    inner.release.set()
    assert inner.sent.wait(timeout=5)
    gateway.shutdown()


class _FailingGateway:
    def send(self, subject: str, body: str, recipients: list[str]) -> str:  # noqa: ARG002
        msg = "SES down"
        raise ConnectionError(msg)


def test_background_gateway_logs_send_failures(caplog: pytest.LogCaptureFixture) -> None:
    gateway = BackgroundEmailGateway(_FailingGateway())
    service = NotificationService(gateway)

    with caplog.at_level(logging.WARNING):
        result = service.dispatch(
            NotificationPayload(
                event=NotificationEvent.BOOKING_CONFIRMED,
                subject="s",
                body="b",
                recipients=["a@x.com"],
            )
        )
        gateway.shutdown()

    assert result.delivered is True  # queued
    assert any("Background e-mail delivery failed" in m for m in caplog.messages)
