import logging

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_config_rejects_insecure_jwt_secret() -> None:
    """D05 - P1: Settings deve falhar em produção se JWT_SECRET for 'change-me'."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(APP_ENV="production", JWT_SECRET="change-me", RESET_SQLITE_ON_STARTUP=False)
    assert "JWT_SECRET cannot be 'change-me' in production" in str(exc_info.value)


def test_production_config_rejects_reset_sqlite_on_startup() -> None:
    """D05 - P1: Settings deve falhar em produção se RESET_SQLITE_ON_STARTUP for True."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            APP_ENV="production",
            JWT_SECRET="secure-real-secret-12345",
            RESET_SQLITE_ON_STARTUP=True,
        )
    assert "RESET_SQLITE_ON_STARTUP cannot be True in production" in str(exc_info.value)


def test_production_config_warns_on_localhost_cors(caplog: pytest.LogCaptureFixture) -> None:
    """D05 - P1: Settings deve emitir um warning se CORS contiver localhost em produção."""
    with caplog.at_level(logging.WARNING):
        Settings(
            APP_ENV="production",
            JWT_SECRET="secure-real-secret-12345",
            RESET_SQLITE_ON_STARTUP=False,
            CORS_ORIGINS="http://localhost:3000,https://linkauto.com",
        )

    assert any("Localhost detected in CORS_ORIGINS" in message for message in caplog.messages)


@pytest.mark.parametrize(
    ("raw_url", "expected"),
    [
        ("postgresql://u:p@db:5432/linkauto", "postgresql+psycopg://u:p@db:5432/linkauto"),
        ("postgres://u:p@db:5432/linkauto", "postgresql+psycopg://u:p@db:5432/linkauto"),
        ("postgresql+psycopg://u:p@db/linkauto", "postgresql+psycopg://u:p@db/linkauto"),
        ("sqlite:///./app.db", "sqlite:///./app.db"),
    ],
)
def test_database_url_uses_the_installed_psycopg_driver(raw_url: str, expected: str) -> None:
    """Plain postgresql:// URLs would make SQLAlchemy load psycopg2, which isn't installed."""
    assert Settings(DATABASE_URL=raw_url).database_url == expected


def test_postgres_url_creates_an_engine_with_psycopg() -> None:
    from sqlalchemy import create_engine  # noqa: PLC0415

    engine = create_engine(Settings(DATABASE_URL="postgresql://u:p@localhost/db").database_url)
    assert engine.dialect.driver == "psycopg"
