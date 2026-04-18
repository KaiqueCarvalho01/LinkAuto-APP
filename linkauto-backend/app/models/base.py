from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def generate_uuid7() -> str:
    uuid7_factory = getattr(uuid, "uuid7", None)
    if callable(uuid7_factory):
        return str(uuid7_factory())
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class UUIDPrimaryKeyMixin:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid7)


class AuditTimestampsMixin:
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
    __abstract__ = True
