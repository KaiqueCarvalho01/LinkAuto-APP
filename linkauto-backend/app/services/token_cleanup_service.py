"""Purge of expired refresh and password reset tokens, run by the scheduled jobs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

from sqlmodel import col, delete

from app.models import PasswordResetToken
from app.models.base import utc_now
from app.services.refresh_token_repository import RefreshTokenRepository

if TYPE_CHECKING:
    from datetime import datetime

    from sqlmodel import Session

# Keep recently expired refresh tokens, so a reused one is still recognised (and its family
# revoked) instead of looking unknown
GRACE_PERIOD = timedelta(days=1)


@dataclass(slots=True)
class TokenCleanupResult:
    """How many expired tokens a run deleted."""

    refresh_tokens_deleted: int
    password_reset_tokens_deleted: int


class TokenCleanupService:
    """Delete tokens that expired more than ``GRACE_PERIOD`` ago. Only flushes."""

    def __init__(self, db: Session) -> None:
        """Bind the service to a session."""
        self._db = db

    def run(self, now: datetime | None = None) -> TokenCleanupResult:
        """Delete expired refresh and password reset tokens past the grace period."""
        cutoff = (now or utc_now()) - GRACE_PERIOD
        refresh = RefreshTokenRepository(self._db).delete_expired(before=cutoff)
        reset = self._db.exec(
            delete(PasswordResetToken).where(col(PasswordResetToken.expires_at) < cutoff)
        ).rowcount
        self._db.flush()
        return TokenCleanupResult(
            refresh_tokens_deleted=refresh, password_reset_tokens_deleted=reset
        )
