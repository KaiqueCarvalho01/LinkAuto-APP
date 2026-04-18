from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import Settings

TokenType = Literal["access", "refresh"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DEFAULT_ALGORITHM = "HS256"


class TokenPayload(BaseModel):
    sub: str
    typ: TokenType
    roles: list[str] = []
    exp: int
    iat: int
    jti: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


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
