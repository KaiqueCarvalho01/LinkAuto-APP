"""Structured logging of security-relevant events (auth, authorization, uploads, admin)."""

import logging

logger = logging.getLogger("app.security")

VISIBLE_TOKEN_CHARS = 4


def mask_token(token: str | None) -> str:
    """Oculta segredos sensíveis exibindo apenas os últimos 4 caracteres.

    Retorna '...' para tokens nulos ou vazios.
    """
    if not token:
        return "..."
    if len(token) <= VISIBLE_TOKEN_CHARS:
        return "..."
    return f"...{token[-VISIBLE_TOKEN_CHARS:]}"


def log_auth_success(email: str, ip: str) -> None:
    """Registra login efetuado com sucesso (INFO)."""
    logger.info(
        "[auth.login.success] User %s logged in successfully from IP %s.",
        email,
        ip,
        extra={"event": "auth.login.success", "email": email, "ip": ip},
    )


def log_auth_failure(email: str, ip: str) -> None:
    """Registra tentativa de login com falha (WARNING)."""
    logger.warning(
        "[auth.login.failure] Failed login attempt for user %s from IP %s.",
        email,
        ip,
        extra={"event": "auth.login.failure", "email": email, "ip": ip},
    )


def log_forbidden(user_id: str, resource: str, ip: str) -> None:
    """Registra tentativa de acesso negado/privilégio insuficiente (WARNING)."""
    logger.warning(
        "[authz.forbidden] Access denied to user %s for resource %s from IP %s.",
        user_id,
        resource,
        ip,
        extra={"event": "authz.forbidden", "user_id": user_id, "resource": resource, "ip": ip},
    )


def log_upload_rejected(user_id: str, reason: str) -> None:
    """Registra upload rejeitado por motivos de validação de arquivo (WARNING)."""
    logger.warning(
        "[upload.rejected] File upload rejected for user %s. Reason: %s.",
        user_id,
        reason,
        extra={"event": "upload.rejected", "user_id": user_id, "reason": reason},
    )


def log_admin_action(admin_id: str, action: str, target_id: str) -> None:
    """Registra ações administrativas sensíveis efetuadas por ADMINs (INFO)."""
    logger.info(
        "[admin.action] Administrator %s performed action '%s' on target %s.",
        admin_id,
        action,
        target_id,
        extra={
            "event": "admin.action",
            "admin_id": admin_id,
            "action": action,
            "target_id": target_id,
        },
    )
