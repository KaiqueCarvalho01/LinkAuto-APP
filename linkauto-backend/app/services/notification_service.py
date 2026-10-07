"""Email notifications for booking and account events, with SES and in-memory gateways."""

from __future__ import annotations

import atexit
import itertools
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol

import boto3

if TYPE_CHECKING:
    from app.core import Settings

logger = logging.getLogger("app.services.notification_service")


class NotificationEvent(StrEnum):
    """Business events that trigger an email notification."""

    INSTRUCTOR_REGISTERED = "instructor_registered_waiting_validation"
    INSTRUCTOR_VALIDATION_DECISION = "instructor_validation_decision"
    NEW_PENDING_BOOKING = "new_pending_booking_for_instructor"
    LESSON_REMINDER_24H = "lesson_reminder_24h_before"
    BOOKING_CONFIRMED = "booking_confirmed_for_student"
    BOOKING_CANCELLED = "booking_cancelled_for_student_instructor"
    NEW_BOOKING_MESSAGE = "new_booking_message"
    NEW_REVIEW_RECEIVED = "new_review_received"


@dataclass(slots=True)
class NotificationPayload:
    """Email notification to send for a given event."""

    event: NotificationEvent
    subject: str
    body: str
    recipients: list[str]


@dataclass(slots=True)
class NotificationDispatchResult:
    """Outcome of a notification dispatch attempt."""

    event: NotificationEvent
    recipients: list[str]
    delivered: bool
    provider_message_id: str | None = None


class EmailGateway(Protocol):
    """Interface for email providers used by ``NotificationService``."""

    def send(self, subject: str, body: str, recipients: list[str]) -> str:
        """Send a plain-text email and return the provider message ID."""
        ...


class SESEmailGateway:
    """Email gateway that sends plain-text emails through AWS SES."""

    def __init__(self, settings: Settings) -> None:
        """Store the configured sender address and create the SES client."""
        self._from_email = settings.ses_from_email
        self._client = boto3.client(
            "ses",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    def send(self, subject: str, body: str, recipients: list[str]) -> str:
        """Send the email via SES and return its message ID.

        Raises ``ValueError`` if no SES sender email is configured.
        """
        if not self._from_email:
            msg = "SES sender email is not configured."
            raise ValueError(msg)

        response = self._client.send_email(
            Source=self._from_email,
            Destination={"ToAddresses": recipients},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )
        return response["MessageId"]


class InMemoryEmailGateway:
    """Email gateway that records messages in memory instead of sending them."""

    def __init__(self) -> None:
        """Initialize an empty list of sent messages."""
        self.sent_messages: list[dict[str, str | list[str]]] = []

    def send(self, subject: str, body: str, recipients: list[str]) -> str:
        """Record the message and return a sequential ``mock-<n>`` message ID."""
        message_id = f"mock-{len(self.sent_messages) + 1}"
        self.sent_messages.append(
            {
                "message_id": message_id,
                "subject": subject,
                "body": body,
                "recipients": recipients,
            }
        )
        return message_id


class EmailDisabledError(RuntimeError):
    """Raised by ``DisabledEmailGateway``: no e-mail provider is configured."""


class DisabledEmailGateway:
    """Gateway used when no e-mail provider is configured: notifications are not sent.

    E-mail is optional, so ``NotificationService`` reports these as not delivered and logs
    them at INFO level instead of treating them as failures.
    """

    def send(self, subject: str, body: str, recipients: list[str]) -> str:  # noqa: ARG002
        """Refuse to send; the caller records the notification as skipped."""
        msg = "E-mail is disabled (no provider configured)."
        raise EmailDisabledError(msg)


class BackgroundEmailGateway:
    """Send e-mails on a small worker pool so a slow provider never delays API responses.

    ``send`` returns a ``queued-<n>`` ID immediately; delivery failures are logged.
    """

    def __init__(self, inner: EmailGateway, *, max_workers: int = 2) -> None:
        """Wrap ``inner`` and start the worker pool."""
        self.inner = inner
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="email")
        self._counter = itertools.count(1)

    def send(self, subject: str, body: str, recipients: list[str]) -> str:
        """Queue the e-mail for delivery and return a local queue ID."""
        self._executor.submit(self._deliver, subject, body, list(recipients))
        return f"queued-{next(self._counter)}"

    def _deliver(self, subject: str, body: str, recipients: list[str]) -> None:
        try:
            self.inner.send(subject=subject, body=body, recipients=recipients)
        except Exception as exc:
            logger.warning(
                "Background e-mail delivery failed",
                extra={"event": "notification.delivery.failure", "error": str(exc)},
                exc_info=True,
            )

    def shutdown(self, *, wait: bool = True) -> None:
        """Stop accepting e-mails and (by default) wait for queued ones to be sent."""
        self._executor.shutdown(wait=wait)


_IN_MEMORY_ENVS = {"development", "test", "ci"}


def build_email_gateway(settings: Settings) -> EmailGateway:
    """Return the e-mail gateway configured by the settings. E-mail is optional.

    - ``EMAIL_BACKEND=ses``, or ``auto`` with ``SES_FROM_EMAIL`` set: SES, sent in the
      background.
    - ``EMAIL_BACKEND=memory``, or ``auto`` in development/test/ci: kept in memory.
    - ``EMAIL_BACKEND=disabled``, or ``auto`` elsewhere without SES: not sent at all.
    """
    backend = settings.email_backend
    if backend == "auto":
        if settings.ses_from_email:
            backend = "ses"
        elif settings.app_env.lower() in _IN_MEMORY_ENVS:
            backend = "memory"
        else:
            backend = "disabled"

    if backend == "memory":
        return InMemoryEmailGateway()
    if backend == "disabled":
        logger.info(
            "E-mail notifications are disabled (no provider configured)",
            extra={"event": "notification.gateway.disabled", "app_env": settings.app_env},
        )
        return DisabledEmailGateway()

    gateway = BackgroundEmailGateway(SESEmailGateway(settings))
    # Flush queued e-mails when the process exits normally
    atexit.register(gateway.shutdown)
    return gateway


class NotificationService:
    """Dispatch notification payloads through an email gateway."""

    def __init__(self, email_gateway: EmailGateway) -> None:
        """Store the email gateway used to deliver notifications."""
        self.email_gateway = email_gateway

    def dispatch(self, payload: NotificationPayload) -> NotificationDispatchResult:
        """Send the payload and report whether it was delivered.

        Gateway errors are logged and never raised; they yield ``delivered=False``. When
        e-mail is disabled the notification is skipped (logged at INFO, not as a failure).
        """
        try:
            message_id = self.email_gateway.send(
                subject=payload.subject,
                body=payload.body,
                recipients=payload.recipients,
            )
            return NotificationDispatchResult(
                event=payload.event,
                recipients=payload.recipients,
                delivered=True,
                provider_message_id=message_id,
            )
        except EmailDisabledError:
            logger.info(
                "Notification skipped, e-mail is disabled [event=%s]",
                payload.event.value,
                extra={
                    "event": "notification.dispatch.skipped",
                    "notification_event": payload.event.value,
                },
            )
            return NotificationDispatchResult(
                event=payload.event,
                recipients=payload.recipients,
                delivered=False,
                provider_message_id=None,
            )
        except Exception as exc:
            logger.warning(
                "Failed to dispatch notification [event=%s]",
                payload.event.value,
                extra={
                    "event": "notification.dispatch.failure",
                    "notification_event": payload.event.value,
                    "error": str(exc),
                },
                exc_info=True,
            )
            return NotificationDispatchResult(
                event=payload.event,
                recipients=payload.recipients,
                delivered=False,
                provider_message_id=None,
            )
