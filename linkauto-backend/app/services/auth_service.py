from __future__ import annotations

from dataclasses import dataclass

from app.core import Settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import UserRole
from app.services.notification_service import NotificationPayload, NotificationService, NotificationEvent
from app.services.us1_store import IdentityStore, UserRecord


@dataclass
class AuthTokens:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthService:
    def __init__(
        self,
        *,
        settings: Settings,
        store: IdentityStore,
        notification_service: NotificationService | None = None,
    ) -> None:
        self._settings = settings
        self._store = store
        self._notification_service = notification_service

    def register(self, *, email: str, password: str, roles: list[str]) -> UserRecord:
        user = self._store.create_user(email=email, password_hash=hash_password(password), roles=roles)

        if self._notification_service and UserRole.INSTRUTOR.value in user.roles:
            self._notification_service.dispatch(
                NotificationPayload(
                    event=NotificationEvent.INSTRUCTOR_REGISTERED,
                    subject="Novo instrutor aguardando validação",
                    body=f"Instrutor {user.email} registrado e aguardando validação administrativa.",
                    recipients=[self._settings.ses_from_email or user.email],
                )
            )
        return user

    def login(self, *, email: str, password: str) -> AuthTokens:
        user = self._store.get_user_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials.")

        access_token = create_access_token(user.id, settings=self._settings, roles=user.roles)
        refresh_token = create_refresh_token(user.id, settings=self._settings, roles=user.roles)
        return AuthTokens(access_token=access_token, refresh_token=refresh_token)

    def refresh(self, *, refresh_token: str) -> AuthTokens:
        payload = decode_token(refresh_token, self._settings, expected_type="refresh")
        user = self._store.get_user(payload.sub)
        if user is None:
            raise ValueError("Invalid refresh token subject.")
        access_token = create_access_token(user.id, settings=self._settings, roles=user.roles)
        rotated_refresh = create_refresh_token(user.id, settings=self._settings, roles=user.roles)
        return AuthTokens(access_token=access_token, refresh_token=rotated_refresh)

    def trigger_password_reset(self, *, email: str) -> None:
        user = self._store.get_user_by_email(email)
        if user is None:
            return
        return None
