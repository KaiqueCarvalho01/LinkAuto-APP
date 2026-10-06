"""Declarative base, primary-key and audit-timestamp mixins shared by all models."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def generate_uuid7() -> str:
    """Return a new UUIDv7 string, falling back to UUIDv4 if uuid7 is unavailable."""
    uuid7_factory = getattr(uuid, "uuid7", None)
    if callable(uuid7_factory):
        return str(uuid7_factory())
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class UUIDPrimaryKeyMixin:
    """Add a 36-char string ``id`` primary key defaulting to a generated UUIDv7."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid7)


class AuditTimestampsMixin:
    """Add non-null UTC ``created_at`` and ``updated_at`` columns (updated on change)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        server_default=func.now(),
    )


class AuditUUIDBase(Base, UUIDPrimaryKeyMixin, AuditTimestampsMixin):
    """Abstract base for models with a UUID primary key and audit timestamps."""

    __abstract__ = True
