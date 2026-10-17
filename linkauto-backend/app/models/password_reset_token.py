"""Single-use password reset tokens, stored only as hashes."""

from datetime import datetime

from sqlalchemy import String
from sqlmodel import Field

from app.models.base import AuditUUIDBase


class PasswordResetToken(AuditUUIDBase, table=True):
    """A password reset link issued to a user.

    Only the SHA-256 hash of the random token is stored, so a database leak does not expose
    working links. A token works once (``used_at``) until ``expires_at``. ``issued_by`` holds
    the admin's ID when an admin generated the link (the fallback while e-mail is disabled);
    like the booking override audit trail, it is deliberately not a foreign key.
    """

    __tablename__ = "password_reset_tokens"

    user_id: str = Field(sa_type=String(36), foreign_key="users.id", ondelete="CASCADE", index=True)
    token_hash: str = Field(sa_type=String(64), unique=True, index=True)
    expires_at: datetime
    used_at: datetime | None = None
    issued_by: str | None = Field(default=None, sa_type=String(36))
