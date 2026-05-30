import logging
from app.core.security_logger import (
    log_auth_success,
    log_auth_failure,
    log_forbidden,
    log_upload_rejected,
    log_admin_action,
    mask_token
)


def test_mask_token_leaves_only_last_four_characters():
    """
    D07 - P2: mask_token deve mascarar segredos exibindo apenas os 4 últimos caracteres.
    """
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIi"
    masked = mask_token(token)
    assert masked.startswith("...")
    assert masked.endswith(token[-4:])
    
    # Se o token for muito curto, deve mascarar de forma segura ou não quebrar
    assert mask_token("abc") == "..."


def test_log_auth_success_emits_structured_info_log(caplog):
    """
    D07 - P2: log_auth_success deve emitir log INFO com dados estruturados.
    """
    with caplog.at_level(logging.INFO):
        log_auth_success("user@example.com", "192.168.1.1")
        
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "INFO"
    assert "auth.login.success" in record.message
    assert "user@example.com" in record.message
    assert "192.168.1.1" in record.message


def test_log_auth_failure_emits_structured_warning_log(caplog):
    """
    D07 - P2: log_auth_failure deve emitir log WARNING com dados estruturados.
    """
    with caplog.at_level(logging.WARNING):
        log_auth_failure("attacker@example.com", "10.0.0.5")
        
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "WARNING"
    assert "auth.login.failure" in record.message
    assert "attacker@example.com" in record.message
    assert "10.0.0.5" in record.message


def test_log_forbidden_emits_structured_warning_log(caplog):
    """
    D07 - P2: log_forbidden deve emitir log WARNING com dados estruturados.
    """
    with caplog.at_level(logging.WARNING):
        log_forbidden("user-123", "/admin/stats", "172.16.0.2")
        
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "WARNING"
    assert "authz.forbidden" in record.message
    assert "user-123" in record.message
    assert "/admin/stats" in record.message
    assert "172.16.0.2" in record.message


def test_log_upload_rejected_emits_structured_warning_log(caplog):
    """
    D07 - P2: log_upload_rejected deve emitir log WARNING com dados estruturados.
    """
    with caplog.at_level(logging.WARNING):
        log_upload_rejected("instructor-456", "INVALID_FILE_CONTENT")
        
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "WARNING"
    assert "upload.rejected" in record.message
    assert "instructor-456" in record.message
    assert "INVALID_FILE_CONTENT" in record.message


def test_log_admin_action_emits_structured_info_log(caplog):
    """
    D07 - P2: log_admin_action deve emitir log INFO com dados estruturados.
    """
    with caplog.at_level(logging.INFO):
        log_admin_action("admin-789", "approve_instructor", "instructor-012")
        
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "INFO"
    assert "admin.action" in record.message
    assert "admin-789" in record.message
    assert "approve_instructor" in record.message
    assert "instructor-012" in record.message
