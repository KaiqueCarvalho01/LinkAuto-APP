from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal
import uuid

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import Settings

TokenType = Literal["access", "refresh"]

DEFAULT_ALGORITHM = "HS256"


class TokenPayload(BaseModel):
    sub: str
    typ: TokenType
    roles: list[str] = []
    exp: int
    iat: int
    jti: str


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def _epoch_seconds(value: datetime) -> int:
    return int(value.timestamp())


def _build_payload(
    subject: str, token_type: TokenType, expires_delta: timedelta, roles: list[str] | None = None
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta
    return {
        "sub": subject,
        "typ": token_type,
        "roles": roles or [],
        "iat": _epoch_seconds(now),
        "exp": _epoch_seconds(expires_at),
        "jti": str(uuid.uuid4()),
    }


def create_access_token(subject: str, settings: Settings, roles: list[str] | None = None) -> str:
    payload = _build_payload(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(minutes=settings.jwt_access_minutes),
        roles=roles,
    )
    return jwt.encode(payload, settings.jwt_secret, algorithm=DEFAULT_ALGORITHM)


def create_refresh_token(subject: str, settings: Settings, roles: list[str] | None = None) -> str:
    payload = _build_payload(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(days=settings.jwt_refresh_days),
        roles=roles,
    )
    return jwt.encode(payload, settings.jwt_secret, algorithm=DEFAULT_ALGORITHM)


def decode_token(token: str, settings: Settings, expected_type: TokenType | None = None) -> TokenPayload:
    try:
        raw_payload = jwt.decode(token, settings.jwt_secret, algorithms=[DEFAULT_ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    payload = TokenPayload.model_validate(raw_payload)
    if expected_type and payload.typ != expected_type:
        raise ValueError(f"Invalid token type: expected {expected_type}")
    return payload
