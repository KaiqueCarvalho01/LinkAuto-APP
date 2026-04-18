from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

import boto3

from app.core import Settings


class NotificationEvent(str, Enum):
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
    event: NotificationEvent
    subject: str
    body: str
    recipients: list[str]


@dataclass(slots=True)
class NotificationDispatchResult:
    event: NotificationEvent
    recipients: list[str]
    delivered: bool
    provider_message_id: str | None = None


class EmailGateway(Protocol):
    def send(self, subject: str, body: str, recipients: list[str]) -> str:
        ...


class SESEmailGateway:
    def __init__(self, settings: Settings) -> None:
        self._from_email = settings.ses_from_email
        self._client = boto3.client(
            "ses",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    def send(self, subject: str, body: str, recipients: list[str]) -> str:
        if not self._from_email:
            raise ValueError("SES sender email is not configured.")

        response = self._client.send_email(
            Source=self._from_email,
            Destination={"ToAddresses": recipients},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )
        return response["MessageId"]


class NotificationService:
    def __init__(self, email_gateway: EmailGateway) -> None:
        self._email_gateway = email_gateway

    def dispatch(self, payload: NotificationPayload) -> NotificationDispatchResult:
        message_id = self._email_gateway.send(
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
