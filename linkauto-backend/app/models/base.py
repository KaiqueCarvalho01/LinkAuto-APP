"""Shared SQLModel bases: UUID primary key and audit timestamps."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import String, func
from sqlmodel import Field, SQLModel


def generate_uuid7() -> str:
    """Return a new UUIDv7 string, falling back to UUIDv4 if uuid7 is unavailable."""
    uuid7_factory = getattr(uuid, "uuid7", None)
    if callable(uuid7_factory):
        return str(uuid7_factory())
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(UTC)


# SQLModel table models share one MetaData; kept under this name for Alembic and tests.
Base = SQLModel


class AuditTimestampsMixin(SQLModel):
    """Add non-null UTC ``created_at`` and ``updated_at`` columns (updated on change)."""

    created_at: datetime = Field(
        default_factory=utc_now, sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column_kwargs={"server_default": func.now(), "onupdate": utc_now},
    )


class AuditUUIDBase(AuditTimestampsMixin):
    """Base for models with a UUIDv7 string primary key and audit timestamps."""

    id: str = Field(default_factory=generate_uuid7, sa_type=String(36), primary_key=True)
