"""Application settings loaded from environment variables and the .env file."""

import logging
from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("app.core.config")

# Placeholder default that must be overridden outside development
INSECURE_JWT_SECRET = "change-me"  # noqa: S105

# psycopg (v3) is the installed PostgreSQL driver; SQLAlchemy defaults bare URLs to psycopg2
_POSTGRES_URL_PREFIXES = ("postgresql://", "postgres://")
POSTGRES_DRIVER_PREFIX = "postgresql+psycopg://"


class Settings(BaseSettings):
    """Typed application settings, each field populated from its upper-case env alias."""

    app_env: str = Field(default="development", alias="APP_ENV")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    app_name: str = Field(default="LinkAuto API", alias="APP_NAME")

    database_url: str = Field(default="sqlite:///./app.db", alias="DATABASE_URL")
    reset_sqlite_on_startup: bool = Field(default=True, alias="RESET_SQLITE_ON_STARTUP")
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )

    jwt_secret: str = Field(default=INSECURE_JWT_SECRET, alias="JWT_SECRET")
    jwt_access_minutes: int = Field(default=15, alias="JWT_ACCESS_MINUTES")
    jwt_refresh_days: int = Field(default=7, alias="JWT_REFRESH_DAYS")

    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    aws_access_key_id: str | None = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str | None = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    s3_bucket: str | None = Field(default=None, alias="S3_BUCKET")
    ses_from_email: str | None = Field(default=None, alias="SES_FROM_EMAIL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("database_url")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        """Rewrite ``postgresql://`` and ``postgres://`` URLs to ``postgresql+psycopg://``."""
        for prefix in _POSTGRES_URL_PREFIXES:
            if value.startswith(prefix):
                return POSTGRES_DRIVER_PREFIX + value.removeprefix(prefix)
        return value

    @model_validator(mode="after")
    def validate_production_security(self) -> Settings:
        """Reject insecure settings when APP_ENV is production.

        Raises if JWT_SECRET is the placeholder or RESET_SQLITE_ON_STARTUP is enabled, and
        logs a warning if CORS_ORIGINS contains localhost or 127.0.0.1.
        """
        if self.app_env.lower() == "production":
            if self.jwt_secret == INSECURE_JWT_SECRET:
                msg = f"JWT_SECRET cannot be {INSECURE_JWT_SECRET!r} in production environment."
                raise ValueError(msg)
            if self.reset_sqlite_on_startup:
                msg = "RESET_SQLITE_ON_STARTUP cannot be True in production environment."
                raise ValueError(msg)

            # CORS checks
            if "localhost" in self.cors_origins.lower() or "127.0.0.1" in self.cors_origins:
                logger.warning(
                    "Localhost detected in CORS_ORIGINS (%s) in production environment!",
                    self.cors_origins,
                )
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        """Return CORS_ORIGINS split on commas, stripped, with empty entries removed."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide cached Settings instance."""
    return Settings()
