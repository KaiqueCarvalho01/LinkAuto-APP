from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.deps import AuthenticatedUser, get_current_user, require_roles
from app.schemas.common import success_response

router = APIRouter(tags=["foundation"])


@router.get("/foundation/ping")
def foundation_ping() -> Response:
    return success_response({"message": "foundation_ok"})


@router.get("/foundation/protected")
def foundation_protected(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> Response:
    data: dict[str, Any] = {"user_id": current_user.user_id, "roles": current_user.roles}
    return success_response(data)


@router.get("/foundation/admin")
def foundation_admin_only(
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN")),
) -> Response:
    return success_response({"user_id": current_user.user_id, "role_check": "ok"})


@router.post("/foundation/conflict")
def foundation_conflict() -> Response:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "code": "CONFLICT",
            "message": "First-write-wins conflict while reserving slots.",
        },
    )
