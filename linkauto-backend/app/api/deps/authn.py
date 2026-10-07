"""Bearer-token authentication dependency."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlmodel import Session  # noqa: TC002 - FastAPI resolves the dependency type at runtime

from app.core import Settings, get_settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    """Identity of the caller: a validated access token for an active, existing account."""

    user_id: str
    roles: list[str]
    token_type: str


def _unauthorized(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "UNAUTHORIZED", "message": message},
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session, Depends(get_db)],
) -> AuthenticatedUser:
    """Return the user identified by the request's bearer access token.

    The account is loaded on every request, so a deactivated or deleted account is
    rejected immediately, and roles come from the database rather than the token (a role
    removed from a user stops applying before the token expires).

    Raises 401 when the token is missing, invalid, expired or not an access token, or when
    its account no longer exists or is inactive.
    """
    if credentials is None:
        msg = "Missing bearer token."
        raise _unauthorized(msg)

    try:
        payload = decode_token(credentials.credentials, settings, expected_type="access")
    except ValueError as exc:
        raise _unauthorized(str(exc)) from exc

    user = db.get(User, payload.sub)
    if user is None or not user.is_active:
        msg = "Invalid token."
        raise _unauthorized(msg)

    return AuthenticatedUser(user_id=user.id, roles=list(user.roles), token_type=payload.typ)
