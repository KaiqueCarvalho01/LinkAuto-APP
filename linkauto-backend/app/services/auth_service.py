"""Authentication service: registration, login, JWT refresh rotation and logout."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import UserRole, generate_uuid7
from app.services.notification_service import (
    NotificationEvent,
    NotificationPayload,
    NotificationService,
)
from app.services.refresh_token_repository import ConsumeResult

logger = logging.getLogger("app.services.auth_service")

if TYPE_CHECKING:
    from app.core import Settings
    from app.models import User
    from app.services.identity_repository import IdentityRepository
    from app.services.refresh_token_repository import RefreshTokenRepository


@dataclass
class AuthTokens:
    """Access/refresh JWT pair returned on login and refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105 - OAuth2 token type, not a secret


class AuthService:
    """Handle user registration, login, refresh token rotation and logout."""

    def __init__(
        self,
        *,
        settings: Settings,
        repository: IdentityRepository,
        refresh_tokens: RefreshTokenRepository,
        notification_service: NotificationService | None = None,
    ) -> None:
        """Store the settings, repositories and optional notification service."""
        self._settings = settings
        self._repository = repository
        self._refresh_tokens = refresh_tokens
        self._notification_service = notification_service

    def register(self, *, email: str, password: str, roles: list[str]) -> User:
        """Register a user with a hashed password.

        Registering an instructor sends a "waiting for validation" notification. Raises
        ``ValueError`` if the ADMIN role is requested or the repository rejects the user.
        """
        if "ADMIN" in [role.upper() for role in roles]:
            msg = "FORBIDDEN_ROLE: Public registration with ADMIN role is not allowed."
            raise ValueError(msg)
        user = self._repository.create_user(
            email=email, password_hash=hash_password(password), roles=roles
        )

        if self._notification_service and UserRole.INSTRUTOR.value in user.roles:
            self._notification_service.dispatch(
                NotificationPayload(
                    event=NotificationEvent.INSTRUCTOR_REGISTERED,
                    subject="Novo instrutor aguardando validação",
                    body=(
                        f"Instrutor {user.email} registrado e aguardando validação administrativa."
                    ),
                    recipients=[self._settings.ses_from_email or user.email],
                )
            )
        return user

    def login(self, *, email: str, password: str) -> AuthTokens:
        """Return new tokens for valid credentials of an active account.

        Raises ``ValueError`` with the same message for an unknown email, a wrong password
        and a deactivated account, so the response doesn't reveal which accounts exist.
        """
        user = self._repository.get_user_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            msg = "Invalid credentials."
            raise ValueError(msg)
        # Checked after the password so a deactivated account can't be probed for existence
        if not user.is_active:
            msg = "Invalid credentials."
            raise ValueError(msg)

        return self._issue_tokens(user)

    def refresh(self, *, refresh_token: str) -> AuthTokens:
        """Consume the refresh token and return a new access token and rotated refresh token.

        Each refresh token works once. Presenting one that was already rotated is treated as
        theft: its whole family (every token descended from the same login) is revoked, so
        both the attacker and the victim must log in again.

        Raises ``ValueError`` if the token is invalid, unknown, revoked or reused, or if its
        subject is not a known, active user.
        """
        payload = decode_token(refresh_token, self._settings, expected_type="refresh")
        user = self._repository.get_user(payload.sub)
        if user is None or not user.is_active:
            msg = "Invalid refresh token subject."
            raise ValueError(msg)

        result, stored = self._refresh_tokens.consume(payload.jti, user_id=user.id)
        if result is ConsumeResult.REUSED:
            logger.warning(
                "Refresh token reuse detected; token family revoked",
                extra={"event": "auth.refresh.reuse", "user_id": user.id},
            )
        if result is not ConsumeResult.OK or stored is None:
            msg = "Invalid refresh token."
            raise ValueError(msg)

        tokens = self._issue_tokens(user, family_id=stored.family_id)
        new_jti = decode_token(tokens.refresh_token, self._settings).jti
        self._refresh_tokens.link_replacement(stored, new_jti)
        return tokens

    def logout(self, *, refresh_token: str | None) -> None:
        """Revoke the refresh token's family (this login session). Invalid tokens are ignored."""
        if not refresh_token:
            return
        try:
            payload = decode_token(refresh_token, self._settings, expected_type="refresh")
        except ValueError:
            return
        stored = self._refresh_tokens.get(payload.jti)
        if stored is not None and stored.user_id == payload.sub:
            self._refresh_tokens.revoke_family(stored.family_id)

    def _issue_tokens(self, user: User, *, family_id: str | None = None) -> AuthTokens:
        access_token = create_access_token(user.id, settings=self._settings, roles=user.roles)
        jti = generate_uuid7()
        refresh_token = create_refresh_token(
            user.id, settings=self._settings, roles=user.roles, jti=jti
        )
        expires_at = datetime.fromtimestamp(decode_token(refresh_token, self._settings).exp, tz=UTC)
        self._refresh_tokens.record(
            jti=jti, user_id=user.id, expires_at=expires_at, family_id=family_id
        )
        return AuthTokens(access_token=access_token, refresh_token=refresh_token)

    def trigger_password_reset(self, *, email: str) -> None:
        """Start a password reset for the email; currently a no-op placeholder."""
        user = self._repository.get_user_by_email(email)
        if user is None:
            return
        return
