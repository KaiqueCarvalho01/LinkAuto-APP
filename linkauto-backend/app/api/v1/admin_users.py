"""Admin endpoints for user accounts."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.deps.types import CurrentAdmin, DbSession
from app.core.security_logger import log_admin_action
from app.schemas.common import success_response
from app.services.dependencies import get_password_reset_service
from app.services.password_reset_service import AdminTargetError, PasswordResetService

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


@router.post("/{user_id}/password-reset-link", status_code=status.HTTP_201_CREATED)
def issue_password_reset_link(
    user_id: str,
    admin_user: CurrentAdmin,
    reset_service: Annotated[PasswordResetService, Depends(get_password_reset_service)],
    db: DbSession,
) -> Response:
    """Issue a password reset link for an admin to hand to the user.

    Requires the ADMIN role. This is the password reset path while e-mail is disabled:
    confirm the user's identity out of band, then send them the returned `reset_url`.
    The link works once, for 24 hours, and replaces any earlier unused link. No e-mail
    is sent and the token is not stored in clear, so it cannot be retrieved again.
    Admin accounts are refused (403), so one admin cannot take over another's account.
    Returns 404 when the user does not exist or is deactivated.
    """
    try:
        link = reset_service.issue_admin_link(user_id, admin_id=admin_user.user_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
    except AdminTargetError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": str(exc)},
        ) from exc
    db.commit()
    log_admin_action(
        admin_id=admin_user.user_id, action="issue_password_reset_link", target_id=user_id
    )
    return success_response(
        {"reset_url": link.url, "expires_at": link.expires_at.isoformat()},
        status_code=status.HTTP_201_CREATED,
    )
