"""Password reset with single-use links, sent by e-mail or issued by an admin."""

from __future__ import annotations

import hashlib
import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from sqlmodel import col, select, update

from app.core.security import hash_password
from app.models import PasswordResetToken
from app.models.base import utc_now
from app.services.notification_templates import EmailTemplateName, render_email

if TYPE_CHECKING:
    from sqlmodel import Session

    from app.core import Settings
    from app.models import User
    from app.services.identity_repository import IdentityRepository
    from app.services.notification_service import NotificationService
    from app.services.refresh_token_repository import RefreshTokenRepository

logger = logging.getLogger("app.services.password_reset_service")

RESET_CONFIRM_PATH = "/password-reset/confirm"
# A link sent by e-mail is used right away; one issued by an admin has to reach the user first
EMAILED_LINK_TTL = timedelta(minutes=30)
ADMIN_LINK_TTL = timedelta(hours=24)
_TOKEN_BYTES = 32


class InvalidResetTokenError(ValueError):
    """Raised for an unknown, expired or already used reset token."""


@dataclass(frozen=True, slots=True)
class ResetLink:
    """A freshly issued reset link; ``url`` holds the only copy of the token."""

    url: str
    expires_at: datetime


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class PasswordResetService:
    """Issue and redeem password reset links. Methods only flush; the caller commits."""

    def __init__(
        self,
        *,
        db: Session,
        settings: Settings,
        repository: IdentityRepository,
        refresh_tokens: RefreshTokenRepository,
        notification_service: NotificationService | None = None,
    ) -> None:
        """Store the session, settings, repositories and optional notification service."""
        self._db = db
        self._settings = settings
        self._repository = repository
        self._refresh_tokens = refresh_tokens
        self._notification_service = notification_service

    def request_reset(self, email: str) -> None:
        """E-mail a reset link to the account with this e-mail, if it exists and is active.

        Does nothing for unknown or deactivated accounts, so callers can always answer the
        same way. Without an e-mail provider the message is skipped; an admin can issue a
        link instead (``issue_admin_link``). In development the link is also logged.
        """
        user = self._repository.get_user_by_email(email)
        if user is None or not user.is_active:
            return
        link = self._issue(user, ttl=EMAILED_LINK_TTL, issued_by=None)
        if self._settings.app_env.lower() == "development":
            logger.info("Password reset link (development only): %s", link.url)
        if self._notification_service is None:
            return
        self._notification_service.dispatch(
            render_email(
                EmailTemplateName.PASSWORD_RESET,
                [user.email],
                link=link.url,
                expires_minutes=str(int(EMAILED_LINK_TTL.total_seconds() // 60)),
            )
        )

    def issue_admin_link(self, user_id: str, *, admin_id: str) -> ResetLink:
        """Return a reset link for an admin to hand to the user (no e-mail is sent).

        Raises ``LookupError`` when the user does not exist or is deactivated.
        """
        user = self._repository.get_user(user_id)
        if user is None or not user.is_active:
            msg = "User not found"
            raise LookupError(msg)
        return self._issue(user, ttl=ADMIN_LINK_TTL, issued_by=admin_id)

    def confirm_reset(self, token: str, new_password: str) -> User:
        """Set a new password with a reset token and sign the user out everywhere.

        The token is consumed with a conditional UPDATE, so it works at most once even when
        submitted twice concurrently. All of the user's refresh tokens are revoked.

        Raises ``InvalidResetTokenError`` for an unknown, expired or used token, or when the
        account was deactivated in the meantime.
        """
        stored = self._db.exec(
            select(PasswordResetToken).where(
                col(PasswordResetToken.token_hash) == _hash_token(token)
            )
        ).first()
        now = utc_now()
        if stored is None or stored.used_at is not None or stored.expires_at <= now:
            raise InvalidResetTokenError(_INVALID)
        user = self._repository.get_user(stored.user_id)
        if user is None or not user.is_active:
            raise InvalidResetTokenError(_INVALID)

        result = self._db.exec(
            update(PasswordResetToken)
            .where(
                col(PasswordResetToken.id) == stored.id,
                col(PasswordResetToken.used_at).is_(None),
            )
            .values(used_at=now)
        )
        if result.rowcount != 1:
            raise InvalidResetTokenError(_INVALID)

        user.password_hash = hash_password(new_password)
        self._refresh_tokens.revoke_all_for_user(user.id)
        self._db.flush()
        return user

    def _issue(self, user: User, *, ttl: timedelta, issued_by: str | None) -> ResetLink:
        # Only the newest link works: retire the user's unused ones
        now = utc_now()
        self._db.exec(
            update(PasswordResetToken)
            .where(
                col(PasswordResetToken.user_id) == user.id,
                col(PasswordResetToken.used_at).is_(None),
            )
            .values(used_at=now)
        )
        token = secrets.token_urlsafe(_TOKEN_BYTES)
        expires_at = now + ttl
        self._db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=_hash_token(token),
                expires_at=expires_at,
                issued_by=issued_by,
            )
        )
        self._db.flush()
        url = self._settings.frontend_link(f"{RESET_CONFIRM_PATH}?{urlencode({'token': token})}")
        return ResetLink(url=url, expires_at=expires_at)


_INVALID = "This password reset link is invalid or has expired."
