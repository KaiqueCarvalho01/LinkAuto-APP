"""Storage of issued refresh tokens: issue, single-use consumption, family revocation."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from sqlmodel import col, select, update

from app.models import RefreshToken, generate_uuid7
from app.models.base import utc_now

if TYPE_CHECKING:
    from datetime import datetime

    from sqlmodel import Session


class ConsumeResult(StrEnum):
    """Outcome of presenting a refresh token."""

    OK = "ok"
    UNKNOWN = "unknown"  # never issued (or already purged)
    REVOKED = "revoked"  # revoked by logout or an earlier reuse detection
    REUSED = "reused"  # already rotated: possible theft, the family is now revoked


class RefreshTokenRepository:
    """Record issued refresh tokens and enforce single use. Methods only flush."""

    def __init__(self, session: Session) -> None:
        """Bind the repository to a session."""
        self._db = session

    def record(
        self, *, jti: str, user_id: str, expires_at: datetime, family_id: str | None = None
    ) -> RefreshToken:
        """Store a newly issued token; a new family is started when ``family_id`` is None."""
        token = RefreshToken(
            jti=jti,
            user_id=user_id,
            family_id=family_id or generate_uuid7(),
            expires_at=expires_at,
        )
        self._db.add(token)
        self._db.flush()
        return token

    def get(self, jti: str) -> RefreshToken | None:
        """Return the stored token with this ``jti``, or ``None``."""
        return self._db.exec(select(RefreshToken).where(col(RefreshToken.jti) == jti)).first()

    def consume(self, jti: str, *, user_id: str) -> tuple[ConsumeResult, RefreshToken | None]:
        """Mark the token as used, exactly once.

        The conditional UPDATE makes concurrent refreshes with the same token (e.g. on two
        workers) succeed at most once. Presenting an already-used token revokes its whole
        family (OWASP refresh token rotation with reuse detection).
        """
        token = self.get(jti)
        if token is None or token.user_id != user_id:
            return ConsumeResult.UNKNOWN, None
        if token.revoked_at is not None:
            return ConsumeResult.REVOKED, token

        now = utc_now()
        result = self._db.exec(
            update(RefreshToken)
            .where(
                col(RefreshToken.id) == token.id,
                col(RefreshToken.used_at).is_(None),
                col(RefreshToken.revoked_at).is_(None),
            )
            .values(used_at=now)
        )
        if result.rowcount == 1:
            self._db.refresh(token)
            return ConsumeResult.OK, token
        # Lost the race or already used: reload to tell a concurrent revocation from reuse
        current = self.get(jti)
        if current is None or current.revoked_at is not None:
            return ConsumeResult.REVOKED, current
        self.revoke_family(current.family_id)
        return ConsumeResult.REUSED, current

    def link_replacement(self, token: RefreshToken, replaced_by_jti: str) -> None:
        """Record which token replaced ``token`` on rotation."""
        token.replaced_by_jti = replaced_by_jti
        self._db.flush()

    def revoke_family(self, family_id: str) -> None:
        """Revoke every not-yet-revoked token of the family."""
        self._db.exec(
            update(RefreshToken)
            .where(
                col(RefreshToken.family_id) == family_id,
                col(RefreshToken.revoked_at).is_(None),
            )
            .values(revoked_at=utc_now())
        )
        self._db.flush()

    def delete_expired(self, *, before: datetime | None = None) -> int:
        """Delete tokens that expired before ``before`` (now by default); return the count."""
        cutoff = before or utc_now()
        stale = self._db.exec(
            select(RefreshToken).where(col(RefreshToken.expires_at) < cutoff)
        ).all()
        for token in stale:
            self._db.delete(token)
        self._db.flush()
        return len(stale)
