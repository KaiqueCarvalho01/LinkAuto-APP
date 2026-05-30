import logging

logger = logging.getLogger("app.security")


def mask_token(token: str | None) -> str:
    """
    Oculta segredos sensíveis exibindo apenas os últimos 4 caracteres.
    Retorna '...' para tokens nulos ou vazios.
    """
    if not token:
        return "..."
    if len(token) <= 4:
        return "..."
    return f"...{token[-4:]}"


def log_auth_success(email: str, ip: str) -> None:
    """Registra login efetuado com sucesso (INFO)."""
    logger.info(
        f"[auth.login.success] User {email} logged in successfully from IP {ip}.",
        extra={
            "event": "auth.login.success",
            "email": email,
            "ip": ip
        }
    )


def log_auth_failure(email: str, ip: str) -> None:
    """Registra tentativa de login com falha (WARNING)."""
    logger.warning(
        f"[auth.login.failure] Failed login attempt for user {email} from IP {ip}.",
        extra={
            "event": "auth.login.failure",
            "email": email,
            "ip": ip
        }
    )


def log_forbidden(user_id: str, resource: str, ip: str) -> None:
    """Registra tentativa de acesso negado/privilégio insuficiente (WARNING)."""
    logger.warning(
        f"[authz.forbidden] Access denied to user {user_id} for resource {resource} from IP {ip}.",
        extra={
            "event": "authz.forbidden",
            "user_id": user_id,
            "resource": resource,
            "ip": ip
        }
    )


def log_upload_rejected(user_id: str, reason: str) -> None:
    """Registra upload rejeitado por motivos de validação de arquivo (WARNING)."""
    logger.warning(
        f"[upload.rejected] File upload rejected for user {user_id}. Reason: {reason}.",
        extra={
            "event": "upload.rejected",
            "user_id": user_id,
            "reason": reason
        }
    )


def log_admin_action(admin_id: str, action: str, target_id: str) -> None:
    """Registra ações administrativas sensíveis efetuadas por ADMINs (INFO)."""
    logger.info(
        f"[admin.action] Administrator {admin_id} performed action '{action}' on target {target_id}.",
        extra={
            "event": "admin.action",
            "admin_id": admin_id,
            "action": action,
            "target_id": target_id
        }
    )
