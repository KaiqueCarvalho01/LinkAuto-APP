"""Issued refresh tokens, for single-use rotation, reuse detection and logout."""

from datetime import datetime

from sqlalchemy import String
from sqlmodel import Field

from app.models.base import AuditUUIDBase


class RefreshToken(AuditUUIDBase, table=True):
    """A refresh token issued to a user, identified by its JWT ``jti``.

    Tokens rotated from the same login share a ``family_id``. A token is used once
    (``used_at``); presenting a used token again revokes the whole family.
    """

    __tablename__ = "refresh_tokens"

    jti: str = Field(sa_type=String(36), unique=True, index=True)
    user_id: str = Field(sa_type=String(36), foreign_key="users.id", ondelete="CASCADE", index=True)
    family_id: str = Field(sa_type=String(36), index=True)
    expires_at: datetime
    used_at: datetime | None = None
    revoked_at: datetime | None = None
    replaced_by_jti: str | None = Field(default=None, sa_type=String(36))
