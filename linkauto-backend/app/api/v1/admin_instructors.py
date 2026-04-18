from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel

from app.api.deps import AuthenticatedUser, require_roles
from app.services.admin_validation_service import AdminValidationService
from app.services.dependencies import get_admin_validation_service
from app.schemas.common import success_response

router = APIRouter(prefix="/admin/instructors", tags=["admin-instructors"])


class RejectInstructorRequest(BaseModel):
    reason: str | None = None


@router.get("")
def list_instructors(
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: AuthenticatedUser = Depends(require_roles("ADMIN")),
    service: AdminValidationService = Depends(get_admin_validation_service),
) -> Response:
    result = service.list_instructors(status=status_filter, page=page, page_size=page_size)
    return success_response(
        result["items"],
        meta={"pagination": {"page": result["page"], "page_size": result["page_size"], "total": result["total"]}},
    )


@router.patch("/{instructor_id}/approve")
def approve_instructor(
    instructor_id: str,
    admin_user: AuthenticatedUser = Depends(require_roles("ADMIN")),
    service: AdminValidationService = Depends(get_admin_validation_service),
) -> Response:
    try:
        result = service.approve(instructor_id=instructor_id, admin_id=admin_user.user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
    return success_response(result.instructor)


@router.patch("/{instructor_id}/reject")
def reject_instructor(
    instructor_id: str,
    payload: RejectInstructorRequest,
    admin_user: AuthenticatedUser = Depends(require_roles("ADMIN")),
    service: AdminValidationService = Depends(get_admin_validation_service),
) -> Response:
    try:
        result = service.reject(
            instructor_id=instructor_id,
            admin_id=admin_user.user_id,
            reason=payload.reason,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
    return success_response(result.instructor)
