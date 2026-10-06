from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel

from app.api.deps.types import CurrentAdmin
from app.core.security_logger import log_admin_action
from app.schemas.common import success_response
from app.services.admin_validation_service import AdminValidationService
from app.services.dependencies import get_admin_validation_service

router = APIRouter(prefix="/admin/instructors", tags=["admin-instructors"])


class RejectInstructorRequest(BaseModel):
    reason: str | None = None


@router.get("")
def list_instructors(
    _: CurrentAdmin,
    service: Annotated[AdminValidationService, Depends(get_admin_validation_service)],
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Response:
    result = service.list_instructors(status=status_filter, page=page, page_size=page_size)
    return success_response(
        result["items"],
        meta={
            "pagination": {
                "page": result["page"],
                "page_size": result["page_size"],
                "total": result["total"],
            }
        },
    )


@router.patch("/{instructor_id}/approve")
def approve_instructor(
    instructor_id: str,
    admin_user: CurrentAdmin,
    service: Annotated[AdminValidationService, Depends(get_admin_validation_service)],
) -> Response:
    try:
        result = service.approve(instructor_id=instructor_id, admin_id=admin_user.user_id)
        log_admin_action(
            admin_id=admin_user.user_id, action="approve_instructor", target_id=instructor_id
        )
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
    admin_user: CurrentAdmin,
    service: Annotated[AdminValidationService, Depends(get_admin_validation_service)],
) -> Response:
    try:
        result = service.reject(
            instructor_id=instructor_id,
            admin_id=admin_user.user_id,
            reason=payload.reason,
        )
        log_admin_action(
            admin_id=admin_user.user_id, action="reject_instructor", target_id=instructor_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
    return success_response(result.instructor)
