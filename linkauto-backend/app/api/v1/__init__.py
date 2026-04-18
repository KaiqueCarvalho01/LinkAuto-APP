from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from app.api.deps import AuthenticatedUser, get_current_user, require_roles
from app.core import Settings, get_settings
from app.core.security import create_access_token, create_refresh_token
from app.schemas.common import success_response

api_v1_router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1)


@api_v1_router.get("/foundation/ping", tags=["foundation"])
def foundation_ping() -> Response:
    return success_response({"message": "foundation_ok"})


@api_v1_router.post("/auth/login", tags=["auth"])
def login(payload: LoginRequest, request: Request, settings: Settings = Depends(get_settings)) -> Response:
    if not payload.email or not payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Invalid credentials."},
        )

    roles = ["ALUNO"]
    if payload.email.endswith("@admin.linkauto"):
        roles.append("ADMIN")

    access_token = create_access_token(payload.email, settings=settings, roles=roles)
    refresh_token = create_refresh_token(payload.email, settings=settings, roles=roles)

    response = success_response(
        {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_minutes * 60,
        }
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.jwt_refresh_days * 24 * 60 * 60,
        path=f"{request.scope.get('root_path', '')}{settings.api_v1_prefix}/auth/refresh",
    )
    return response


@api_v1_router.get("/foundation/protected", tags=["foundation"])
def foundation_protected(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> Response:
    data: dict[str, Any] = {"user_id": current_user.user_id, "roles": current_user.roles}
    return success_response(data)


@api_v1_router.get("/foundation/admin", tags=["foundation"])
def foundation_admin_only(
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN")),
) -> Response:
    return success_response({"user_id": current_user.user_id, "role_check": "ok"})


@api_v1_router.post("/foundation/conflict", tags=["foundation"])
def foundation_conflict() -> Response:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "code": "CONFLICT",
            "message": "First-write-wins conflict while reserving slots.",
        },
    )
