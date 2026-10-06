"""Bearer-token authentication dependency."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core import Settings, get_settings
from app.core.security import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    """Identity extracted from a validated access token."""

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
) -> AuthenticatedUser:
    """Return the user identified by the request's bearer access token.

    Raises 401 when the token is missing, invalid, expired or not an access token.
    """
    if credentials is None:
        msg = "Missing bearer token."
        raise _unauthorized(msg)

    try:
        payload = decode_token(credentials.credentials, settings, expected_type="access")
    except ValueError as exc:
        raise _unauthorized(str(exc)) from exc

    return AuthenticatedUser(user_id=payload.sub, roles=payload.roles, token_type=payload.typ)
