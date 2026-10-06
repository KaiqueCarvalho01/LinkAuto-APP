"""Email notifications for booking and account events, with SES and in-memory gateways."""

from __future__ import annotations

import logging
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


class NotificationService:
    """Dispatch notification payloads through an email gateway."""

    def __init__(self, email_gateway: EmailGateway) -> None:
        """Store the email gateway used to deliver notifications."""
        self.email_gateway = email_gateway

    def dispatch(self, payload: NotificationPayload) -> NotificationDispatchResult:
        """Send the payload and report whether it was delivered.

        Gateway errors are logged and never raised; they yield ``delivered=False``.
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
