from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from app.core import Settings, get_settings
from app.services.auth_service import AuthService
from app.services.dependencies import get_auth_service, get_profile_service
from app.services.profile_service import ProfileService
from app.schemas.common import success_response

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=8)
    roles: list[str] = Field(min_length=1)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


class PasswordResetRequest(BaseModel):
    email: str = Field(min_length=3)


def _set_refresh_cookie(
    response: Response, *, refresh_token: str, request: Request, settings: Settings
) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.jwt_refresh_days * 24 * 60 * 60,
        path=f"{request.scope.get('root_path', '')}{settings.api_v1_prefix}/auth/refresh",
    )


@router.post("/register")
def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
    profile_service: ProfileService = Depends(get_profile_service),
) -> Response:
    try:
        user = auth_service.register(email=payload.email, password=payload.password, roles=payload.roles)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": str(exc)},
        ) from exc
    return success_response(profile_service.get_me(user.id), status_code=status.HTTP_201_CREATED)


@router.post("/login")
def login(
    payload: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
) -> Response:
    try:
        tokens = auth_service.login(email=payload.email, password=payload.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": str(exc)},
        ) from exc

    response = success_response(
        {
            "access_token": tokens.access_token,
            "token_type": tokens.token_type,
            "expires_in": settings.jwt_access_minutes * 60,
        }
    )
    _set_refresh_cookie(response, refresh_token=tokens.refresh_token, request=request, settings=settings)
    return response


@router.post("/refresh")
def refresh(
    request: Request,
    refresh_token: str | None = Cookie(default=None),
    auth_service: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
) -> Response:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Missing refresh token cookie."},
        )
    try:
        tokens = auth_service.refresh(refresh_token=refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": str(exc)},
        ) from exc

    response = success_response(
        {
            "access_token": tokens.access_token,
            "token_type": tokens.token_type,
            "expires_in": settings.jwt_access_minutes * 60,
        }
    )
    _set_refresh_cookie(response, refresh_token=tokens.refresh_token, request=request, settings=settings)
    return response


@router.post("/password-reset")
def password_reset(
    payload: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> Response:
    auth_service.trigger_password_reset(email=payload.email)
    return success_response({"status": "accepted"}, status_code=status.HTTP_202_ACCEPTED)
