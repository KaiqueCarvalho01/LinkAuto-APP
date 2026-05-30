import logging
from app.services.notification_service import (
    NotificationService,
    NotificationPayload,
    NotificationEvent,
    NotificationDispatchResult
)


class FailureEmailGateway:
    """Mock email gateway that always fails."""
    def send(self, subject: str, body: str, recipients: list[str]) -> str:
        raise ConnectionError("Gateway is offline")


def test_notification_service_handles_gateway_failure(caplog):
    """
    D11 - P1: Resiliência do NotificationService
    Verifica se o serviço captura falhas do gateway de e-mail e não propaga a exceção,
    retornando delivered=False e gerando logs adequados.
    """
    gateway = FailureEmailGateway()
    service = NotificationService(email_gateway=gateway)
    
    payload = NotificationPayload(
        event=NotificationEvent.NEW_PENDING_BOOKING,
        subject="Novo agendamento pendente",
        body="Você possui um novo agendamento para confirmar.",
        recipients=["instructor@example.com"]
    )
    
    with caplog.at_level(logging.WARNING):
        result = service.dispatch(payload)
        
    assert isinstance(result, NotificationDispatchResult)
    assert result.delivered is False
    assert result.provider_message_id is None
    
    # Valida que um log warning de falha contendo o evento foi emitido
    assert any(
        "notification.dispatch.failure" in message or "Failed to dispatch notification" in message
        for message in caplog.messages
    )
