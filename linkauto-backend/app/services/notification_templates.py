"""Subject and body of every notification e-mail, kept in one place.

Templates are ``str.format`` strings filled with named values (``{student_name}``...). Values
are inserted as-is and never formatted again, so user text such as a message containing
``{braces}`` is safe. Internal IDs must not be passed in: e-mails use names, lesson times and
links to the frontend instead. Every body ends with the same signature.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.models.booking import CancelledBy
from app.services.notification_service import NotificationEvent, NotificationPayload

SIGNATURE = "\n\nEquipe LinkAuto"


class EmailTemplateName(StrEnum):
    """Every e-mail the application sends."""

    INSTRUCTOR_REGISTERED = "instructor_registered"
    INSTRUCTOR_APPROVED = "instructor_approved"
    INSTRUCTOR_REJECTED = "instructor_rejected"
    BOOKING_REQUESTED = "booking_requested"
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_CANCELLED = "booking_cancelled"
    LESSON_REMINDER = "lesson_reminder"
    BOOKING_MESSAGE = "booking_message"
    REVIEW_RECEIVED = "review_received"


@dataclass(frozen=True, slots=True)
class EmailTemplate:
    """Plain-text e-mail for a notification event."""

    event: NotificationEvent
    subject: str
    body: str


TEMPLATES: dict[EmailTemplateName, EmailTemplate] = {
    EmailTemplateName.INSTRUCTOR_REGISTERED: EmailTemplate(
        event=NotificationEvent.INSTRUCTOR_REGISTERED,
        subject="Novo instrutor aguardando validação",
        body=(
            "{instructor_email} se cadastrou como instrutor e aguarda a validação das "
            "credenciais.\n\nRevise em: {link}"
        ),
    ),
    EmailTemplateName.INSTRUCTOR_APPROVED: EmailTemplate(
        event=NotificationEvent.INSTRUCTOR_VALIDATION_DECISION,
        subject="Seu credenciamento foi aprovado",
        body=(
            "Olá, {recipient_name}!\n\nSeu credenciamento como instrutor no LinkAuto foi "
            "aprovado, e seu perfil já aparece nas buscas.\n\nAcesse: {link}"
        ),
    ),
    EmailTemplateName.INSTRUCTOR_REJECTED: EmailTemplate(
        event=NotificationEvent.INSTRUCTOR_VALIDATION_DECISION,
        subject="Seu credenciamento não foi aprovado",
        body=(
            "Olá, {recipient_name}!\n\nSeu credenciamento como instrutor no LinkAuto não foi "
            "aprovado.\nMotivo: {reason}\n\nRevise seus dados e documentos em: {link}"
        ),
    ),
    EmailTemplateName.BOOKING_REQUESTED: EmailTemplate(
        event=NotificationEvent.NEW_PENDING_BOOKING,
        subject="Nova solicitação de aula de {student_name}",
        body=(
            "Olá, {recipient_name}!\n\n{student_name} solicitou uma aula com você em "
            "{lesson_time}.\n\nSolicitações não confirmadas em 24 horas são canceladas "
            "automaticamente. Confirme ou recuse em: {link}"
        ),
    ),
    EmailTemplateName.BOOKING_CONFIRMED: EmailTemplate(
        event=NotificationEvent.BOOKING_CONFIRMED,
        subject="Aula confirmada com {instructor_name}",
        body=(
            "Olá, {recipient_name}!\n\n{instructor_name} confirmou sua aula em {lesson_time}."
            "\n\nVeja os detalhes em: {link}"
        ),
    ),
    EmailTemplateName.BOOKING_CANCELLED: EmailTemplate(
        event=NotificationEvent.BOOKING_CANCELLED,
        subject="Aula cancelada: {lesson_time}",
        body=(
            "Olá, {recipient_name}!\n\nSua aula com {other_name} em {lesson_time} foi "
            "cancelada {cancelled_by}.\nMotivo: {reason}\n\nVeja suas aulas em: {link}"
        ),
    ),
    EmailTemplateName.LESSON_REMINDER: EmailTemplate(
        event=NotificationEvent.LESSON_REMINDER_24H,
        subject="Lembrete: sua aula com {other_name} é amanhã",
        body=(
            "Olá, {recipient_name}!\n\nSua aula com {other_name} será em {lesson_time}."
            "\n\nVeja os detalhes em: {link}"
        ),
    ),
    EmailTemplateName.BOOKING_MESSAGE: EmailTemplate(
        event=NotificationEvent.NEW_BOOKING_MESSAGE,
        subject="Nova mensagem de {sender_name}",
        body=(
            "Olá, {recipient_name}!\n\n{sender_name} enviou uma mensagem sobre a aula de "
            '{lesson_time}:\n\n"{content}"\n\nResponda em: {link}'
        ),
    ),
    EmailTemplateName.REVIEW_RECEIVED: EmailTemplate(
        event=NotificationEvent.NEW_REVIEW_RECEIVED,
        subject="Nova avaliação de {reviewer_name}",
        body=(
            "Olá, {recipient_name}!\n\n{reviewer_name} avaliou a aula de {lesson_time} com "
            "{rating} de 5 estrelas.\nComentário: {comment}\n\nVeja em: {link}"
        ),
    ),
}

# Completes "foi cancelada {cancelled_by}" in BOOKING_CANCELLED
CANCELLED_BY_LABELS: dict[str, str] = {
    CancelledBy.ALUNO.value: "por {student_name}",
    CancelledBy.INSTRUTOR.value: "por {instructor_name}",
    CancelledBy.SISTEMA.value: "automaticamente, porque não foi confirmada em 24 horas",
    CancelledBy.ADMIN.value: "pela administração do LinkAuto",
}

NO_REASON = "não informado"
NO_COMMENT = "sem comentário"


def render_email(
    name: EmailTemplateName, recipients: list[str], **values: str
) -> NotificationPayload:
    """Fill the named template with ``values`` and return the payload to dispatch.

    Raises ``KeyError`` when the template needs a value that was not given.
    """
    template = TEMPLATES[name]
    return NotificationPayload(
        event=template.event,
        subject=template.subject.format_map(values),
        body=template.body.format_map(values) + SIGNATURE,
        recipients=recipients,
    )
