from functools import lru_cache
import logging

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("app.core.config")


class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    app_name: str = Field(default="LinkAuto API", alias="APP_NAME")

    database_url: str = Field(default="sqlite:///./app.db", alias="DATABASE_URL")
    reset_sqlite_on_startup: bool = Field(default=True, alias="RESET_SQLITE_ON_STARTUP")
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )

    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    jwt_access_minutes: int = Field(default=15, alias="JWT_ACCESS_MINUTES")
    jwt_refresh_days: int = Field(default=7, alias="JWT_REFRESH_DAYS")

    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    aws_access_key_id: str | None = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str | None = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    s3_bucket: str | None = Field(default=None, alias="S3_BUCKET")
    ses_from_email: str | None = Field(default=None, alias="SES_FROM_EMAIL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.app_env.lower() == "production":
            if self.jwt_secret == "change-me":
                raise ValueError("JWT_SECRET cannot be 'change-me' in production environment.")
            if self.reset_sqlite_on_startup:
                raise ValueError("RESET_SQLITE_ON_STARTUP cannot be True in production environment.")
            
            # CORS checks
            if "localhost" in self.cors_origins.lower() or "127.0.0.1" in self.cors_origins:
                logger.warning(
                    f"Localhost detected in CORS_ORIGINS ({self.cors_origins}) in production environment!"
                )
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
