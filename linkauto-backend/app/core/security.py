"""Password hashing (bcrypt) and JWT access/refresh token handling."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, Literal

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel

if TYPE_CHECKING:
    from app.core.config import Settings

TokenType = Literal["access", "refresh"]

DEFAULT_ALGORITHM = "HS256"


class TokenPayload(BaseModel):
    """Decoded JWT claims: subject user ID, token type, roles, expiry, issued-at and token ID."""

    sub: str
    typ: TokenType
    roles: list[str] = []
    exp: int
    iat: int
    jti: str


BCRYPT_MAX_PASSWORD_BYTES = 72


def _password_bytes(password: str) -> bytes:
    # bcrypt only uses the first 72 bytes. bcrypt<5 truncated silently; bcrypt>=5 raises instead.
    # Truncate explicitly to keep existing hashes and long passwords working.
    return password.encode("utf-8")[:BCRYPT_MAX_PASSWORD_BYTES]


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the password (only its first 72 bytes are used)."""
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Return whether the password matches the stored bcrypt hash."""
    return bcrypt.checkpw(_password_bytes(plain_password), password_hash.encode("utf-8"))


def _epoch_seconds(value: datetime) -> int:
    return int(value.timestamp())


def _build_payload(
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
    roles: list[str] | None = None,
    jti: str | None = None,
) -> dict[str, Any]:
    now = datetime.now(UTC)
    expires_at = now + expires_delta
    return {
        "sub": subject,
        "typ": token_type,
        "roles": roles or [],
        "iat": _epoch_seconds(now),
        "exp": _epoch_seconds(expires_at),
        "jti": jti or str(uuid.uuid4()),
    }


def create_access_token(subject: str, settings: Settings, roles: list[str] | None = None) -> str:
    """Return a signed access JWT that expires after JWT_ACCESS_MINUTES."""
    payload = _build_payload(
        subject=subject,
        token_type="access",  # noqa: S106 - token kind, not a secret
        expires_delta=timedelta(minutes=settings.jwt_access_minutes),
        roles=roles,
    )
    return jwt.encode(payload, settings.jwt_secret, algorithm=DEFAULT_ALGORITHM)


def create_refresh_token(
    subject: str, settings: Settings, roles: list[str] | None = None, *, jti: str | None = None
) -> str:
    """Return a signed refresh JWT that expires after JWT_REFRESH_DAYS.

    ``jti`` sets the token ID (a random UUID by default), so the caller can record it.
    """
    payload = _build_payload(
        subject=subject,
        token_type="refresh",  # noqa: S106 - token kind, not a secret
        expires_delta=timedelta(days=settings.jwt_refresh_days),
        roles=roles,
        jti=jti,
    )
    return jwt.encode(payload, settings.jwt_secret, algorithm=DEFAULT_ALGORITHM)


def decode_token(
    token: str, settings: Settings, expected_type: TokenType | None = None
) -> TokenPayload:
    """Verify and decode a JWT into a TokenPayload.

    Raises ValueError if the token is invalid or not of ``expected_type`` (when given).
    """
    try:
        raw_payload = jwt.decode(token, settings.jwt_secret, algorithms=[DEFAULT_ALGORITHM])
    except JWTError as exc:
        msg = "Invalid token"
        raise ValueError(msg) from exc

    payload = TokenPayload.model_validate(raw_payload)
    if expected_type and payload.typ != expected_type:
        msg = f"Invalid token type: expected {expected_type}"
        raise ValueError(msg)
    return payload
