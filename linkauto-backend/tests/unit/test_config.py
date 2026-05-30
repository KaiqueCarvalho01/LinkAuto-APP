import pytest
from pydantic import ValidationError
import logging
from app.core.config import Settings


def test_production_config_rejects_insecure_jwt_secret():
    """
    D05 - P1: Settings deve falhar em produção se JWT_SECRET for 'change-me'
    """
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            APP_ENV="production",
            JWT_SECRET="change-me",
            RESET_SQLITE_ON_STARTUP=False
        )
    assert "JWT_SECRET cannot be 'change-me' in production" in str(exc_info.value)


def test_production_config_rejects_reset_sqlite_on_startup():
    """
    D05 - P1: Settings deve falhar em produção se RESET_SQLITE_ON_STARTUP for True
    """
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            APP_ENV="production",
            JWT_SECRET="secure-real-secret-12345",
            RESET_SQLITE_ON_STARTUP=True
        )
    assert "RESET_SQLITE_ON_STARTUP cannot be True in production" in str(exc_info.value)


def test_production_config_warns_on_localhost_cors(caplog):
    """
    D05 - P1: Settings deve emitir um warning se CORS contiver localhost em produção
    """
    with caplog.at_level(logging.WARNING):
        Settings(
            APP_ENV="production",
            JWT_SECRET="secure-real-secret-12345",
            RESET_SQLITE_ON_STARTUP=False,
            CORS_ORIGINS="http://localhost:3000,https://linkauto.com"
        )
    
    assert any(
        "Localhost detected in CORS_ORIGINS" in message
        for message in caplog.messages
    )
