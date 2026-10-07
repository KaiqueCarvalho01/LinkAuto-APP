"""Authentication service: registration, login and JWT refresh."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import UserRole
from app.services.notification_service import (
    NotificationEvent,
    NotificationPayload,
    NotificationService,
)

if TYPE_CHECKING:
    from app.core import Settings
    from app.models import User
    from app.services.identity_repository import IdentityRepository


@dataclass
class AuthTokens:
    """Access/refresh JWT pair returned on login and refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105 - OAuth2 token type, not a secret


class AuthService:
    """Handle user registration, login and token refresh."""

    def __init__(
        self,
        *,
        settings: Settings,
        repository: IdentityRepository,
        notification_service: NotificationService | None = None,
    ) -> None:
        """Store the settings, identity repository and optional notification service."""
        self._settings = settings
        self._repository = repository
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
        """Return new tokens for valid credentials, raising ``ValueError`` otherwise."""
        user = self._repository.get_user_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            msg = "Invalid credentials."
            raise ValueError(msg)

        access_token = create_access_token(user.id, settings=self._settings, roles=user.roles)
        refresh_token = create_refresh_token(user.id, settings=self._settings, roles=user.roles)
        return AuthTokens(access_token=access_token, refresh_token=refresh_token)

    def refresh(self, *, refresh_token: str) -> AuthTokens:
        """Return a new access token and a rotated refresh token.

        Raises ``ValueError`` if the token's subject does not match a known user.
        """
        payload = decode_token(refresh_token, self._settings, expected_type="refresh")
        user = self._repository.get_user(payload.sub)
        if user is None:
            msg = "Invalid refresh token subject."
            raise ValueError(msg)
        access_token = create_access_token(user.id, settings=self._settings, roles=user.roles)
        rotated_refresh = create_refresh_token(user.id, settings=self._settings, roles=user.roles)
        return AuthTokens(access_token=access_token, refresh_token=rotated_refresh)

    def trigger_password_reset(self, *, email: str) -> None:
        """Start a password reset for the email; currently a no-op placeholder."""
        user = self._repository.get_user_by_email(email)
        if user is None:
            return
        return
