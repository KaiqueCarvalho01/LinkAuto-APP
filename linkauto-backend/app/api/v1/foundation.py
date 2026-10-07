"""Diagnostic endpoints for verifying the API envelope, auth and error handling."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.api.deps.types import CurrentAdmin, CurrentUser
from app.core.rate_limit import client_ip
from app.schemas.common import success_response

router = APIRouter(tags=["foundation"])


@router.get("/foundation/ping")
def foundation_ping() -> Response:
    """Return a static success payload to check that the API is reachable."""
    return success_response({"message": "foundation_ok"})


@router.get("/foundation/whoami")
def foundation_whoami(request: Request) -> Response:
    """Return the client IP the API sees (after trusted-proxy resolution), for diagnostics."""
    return success_response({"client_ip": client_ip(request)})


@router.get("/foundation/protected")
def foundation_protected(
    current_user: CurrentUser,
) -> Response:
    """Return the caller's user ID and roles.

    Requires authentication; returns 401 without a valid access token.
    """
    data: dict[str, Any] = {"user_id": current_user.user_id, "roles": current_user.roles}
    return success_response(data)


@router.get("/foundation/admin")
def foundation_admin_only(
    current_user: CurrentAdmin,
) -> Response:
    """Confirm that the caller holds the ADMIN role.

    Returns 401 when unauthenticated and 403 for non-admin users.
    """
    return success_response({"user_id": current_user.user_id, "role_check": "ok"})


@router.post("/foundation/conflict")
def foundation_conflict() -> Response:
    """Raise a 409 conflict to exercise the error envelope; always fails."""
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "code": "CONFLICT",
            "message": "First-write-wins conflict while reserving slots.",
        },
    )
