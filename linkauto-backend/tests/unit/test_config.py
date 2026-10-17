import logging

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.services.document_storage import LocalDocumentStorage, build_document_storage


def test_production_config_rejects_insecure_jwt_secret() -> None:
    """D05 - P1: Settings deve falhar em produção se JWT_SECRET for 'change-me'."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(APP_ENV="production", JWT_SECRET="change-me", RESET_SQLITE_ON_STARTUP=False)
    assert "JWT_SECRET cannot be 'change-me' outside development" in str(exc_info.value)


def test_production_config_rejects_reset_sqlite_on_startup() -> None:
    """D05 - P1: Settings deve falhar em produção se RESET_SQLITE_ON_STARTUP for True."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            APP_ENV="production",
            JWT_SECRET="secure-real-secret-12345",
            RESET_SQLITE_ON_STARTUP=True,
        )
    assert "RESET_SQLITE_ON_STARTUP cannot be True outside development" in str(exc_info.value)


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


@pytest.mark.parametrize("app_env", ["staging", "prod", "Production ", "produciton", ""])
def test_any_non_development_env_rejects_insecure_defaults(app_env: str) -> None:
    """#79: the checks fail closed, not only for APP_ENV exactly "production"."""
    with pytest.raises(ValidationError, match="JWT_SECRET cannot be"):
        Settings(APP_ENV=app_env, RESET_SQLITE_ON_STARTUP=False)
    with pytest.raises(ValidationError, match="RESET_SQLITE_ON_STARTUP cannot be True"):
        Settings(APP_ENV=app_env, JWT_SECRET="secure-real-secret-12345")


@pytest.mark.parametrize("app_env", ["development", "test", "ci", "CI"])
def test_development_like_envs_keep_the_defaults(app_env: str) -> None:
    settings = Settings(APP_ENV=app_env)

    assert settings.is_development_like
    assert settings.jwt_secret == "change-me"


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


def test_production_config_does_not_require_s3() -> None:
    """S3 is optional: without a bucket, documents are kept on the local disk."""
    settings = Settings(
        APP_ENV="production",
        JWT_SECRET="secure-real-secret-12345",
        RESET_SQLITE_ON_STARTUP=False,
    )

    assert settings.s3_bucket is None
    assert isinstance(build_document_storage(settings), LocalDocumentStorage)
