"""Authentication endpoints: registration, login, token refresh, logout, password reset."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from app.api.deps.types import AppSettings, DbSession
from app.core.rate_limit import limiter
from app.core.security_logger import log_auth_failure, log_auth_success
from app.schemas.common import success_response
from app.services.auth_service import AuthService
from app.services.dependencies import get_auth_service, get_profile_service
from app.services.profile_service import ProfileService

if TYPE_CHECKING:
    from app.core import Settings

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    """Credentials and requested roles for a new account."""

    email: str = Field(min_length=3)
    password: str = Field(min_length=8)
    roles: list[str] = Field(min_length=1)


class LoginRequest(BaseModel):
    """Email and password credentials for logging in."""

    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


class PasswordResetRequest(BaseModel):
    """Email address of the account requesting a password reset."""

    email: str = Field(min_length=3)


REFRESH_COOKIE = "refresh_token"


def _refresh_cookie_path(request: Request, settings: Settings) -> str:
    # Sent only to the auth endpoints that need it: /auth/refresh and /auth/logout
    return f"{request.scope.get('root_path', '')}{settings.api_v1_prefix}/auth"


def _set_refresh_cookie(
    response: Response, *, refresh_token: str, request: Request, settings: Settings
) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.jwt_refresh_days * 24 * 60 * 60,
        path=_refresh_cookie_path(request, settings),
    )


@router.post("/register")
@limiter.limit("5/minute")
def register(
    request: Request,  # noqa: ARG001 - required by slowapi's @limiter.limit
    payload: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    db: DbSession,
) -> Response:
    """Register a new user account and return its profile.

    Public; rate-limited to 5 requests per minute. Registering with the ADMIN role
    is not allowed. Returns 400 for a duplicate email, unsupported or forbidden roles.
    """
    try:
        user = auth_service.register(
            email=payload.email, password=payload.password, roles=payload.roles
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": str(exc)},
        ) from exc
    profile = profile_service.get_me(user.id)
    db.commit()
    return success_response(profile, status_code=status.HTTP_201_CREATED)


@router.post("/login")
@limiter.limit("10/minute")
def login(
    payload: LoginRequest,
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    settings: AppSettings,
    db: DbSession,
) -> Response:
    """Authenticate with email and password and issue tokens.

    Public; rate-limited to 10 requests per minute. Returns a bearer access token in
    the body and sets the refresh token as an HTTP-only cookie scoped to the auth
    endpoints. Returns 401 for invalid credentials or a deactivated account.
    """
    client_ip = request.client.host if request.client else "unknown"
    try:
        tokens = auth_service.login(email=payload.email, password=payload.password)
        log_auth_success(email=payload.email, ip=client_ip)
    except ValueError as exc:
        log_auth_failure(email=payload.email, ip=client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": str(exc)},
        ) from exc
    db.commit()

    response = success_response(
        {
            "access_token": tokens.access_token,
            "token_type": tokens.token_type,
            "expires_in": settings.jwt_access_minutes * 60,
        }
    )
    _set_refresh_cookie(
        response, refresh_token=tokens.refresh_token, request=request, settings=settings
    )
    return response


@router.post("/refresh")
@limiter.limit("20/minute")
def refresh(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    settings: AppSettings,
    db: DbSession,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> Response:
    """Issue a new access token using the refresh token cookie.

    Rate-limited to 20 requests per minute. Each refresh token works once: it is
    rotated and the new one is set as a cookie. Presenting an already-rotated token
    revokes every token of that login session (reuse detection). Returns 401 when the
    cookie is missing or the token is invalid, revoked or reused.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Missing refresh token cookie."},
        )
    try:
        tokens = auth_service.refresh(refresh_token=refresh_token)
    except ValueError as exc:
        # Keep the reuse-detection revocation even though the request fails
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": str(exc)},
        ) from exc
    db.commit()

    response = success_response(
        {
            "access_token": tokens.access_token,
            "token_type": tokens.token_type,
            "expires_in": settings.jwt_access_minutes * 60,
        }
    )
    _set_refresh_cookie(
        response, refresh_token=tokens.refresh_token, request=request, settings=settings
    )
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    settings: AppSettings,
    db: DbSession,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> Response:
    """Revoke the refresh token of this session and clear its cookie.

    Public (the refresh cookie identifies the session). Always returns 204, also when
    the cookie is missing or invalid. Access tokens already issued stay valid until
    they expire (15 minutes by default).
    """
    auth_service.logout(refresh_token=refresh_token)
    db.commit()
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        key=REFRESH_COOKIE,
        path=_refresh_cookie_path(request, settings),
        secure=True,
        httponly=True,
        samesite="strict",
    )
    return response


@router.post("/password-reset")
@limiter.limit("3/minute")
def password_reset(
    request: Request,  # noqa: ARG001 - required by slowapi's @limiter.limit
    payload: PasswordResetRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Response:
    """Accept a password reset request for the given email.

    Public; rate-limited to 3 requests per minute. Always returns 202 so that the
    response does not reveal whether the email is registered.
    """
    auth_service.trigger_password_reset(email=payload.email)
    return success_response({"status": "accepted"}, status_code=status.HTTP_202_ACCEPTED)
