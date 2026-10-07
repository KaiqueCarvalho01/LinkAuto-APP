"""Admin endpoints for reviewing instructor credentials."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel

from app.api.deps.types import CurrentAdmin, DbSession
from app.core.security_logger import log_admin_action
from app.schemas.common import success_response
from app.services.admin_validation_service import AdminValidationService
from app.services.dependencies import (
    get_admin_validation_service,
    get_instructor_document_service,
)
from app.services.instructor_document_service import InstructorDocumentService

router = APIRouter(prefix="/admin/instructors", tags=["admin-instructors"])


class RejectInstructorRequest(BaseModel):
    """Payload for rejecting an instructor, with an optional reason."""

    reason: str | None = None


@router.get("")
def list_instructors(
    _: CurrentAdmin,
    service: Annotated[AdminValidationService, Depends(get_admin_validation_service)],
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Response:
    """List instructors with pagination, optionally filtered by validation status.

    Requires the ADMIN role. Pagination details are returned in `meta.pagination`.
    """
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


@router.get("/{instructor_id}/documents")
def list_instructor_documents(
    instructor_id: str,
    admin_user: CurrentAdmin,
    service: Annotated[InstructorDocumentService, Depends(get_instructor_document_service)],
) -> Response:
    """List an instructor's submitted documents with short-lived links to view them.

    Requires the ADMIN role. Each link expires after `expires_in` seconds (5 minutes).
    Documents are deleted once the instructor is approved or rejected.
    """
    log_admin_action(
        admin_id=admin_user.user_id, action="view_instructor_documents", target_id=instructor_id
    )
    return success_response(service.list_for_review(instructor_id))


@router.patch("/{instructor_id}/approve")
def approve_instructor(
    instructor_id: str,
    admin_user: CurrentAdmin,
    service: Annotated[AdminValidationService, Depends(get_admin_validation_service)],
    db: DbSession,
) -> Response:
    """Approve an instructor's credentials.

    Requires the ADMIN role. Marks the instructor as APROVADO, purges the uploaded
    documents, notifies the instructor and returns the updated user. Returns 404
    when the instructor does not exist.
    """
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
    db.commit()
    return success_response(result.instructor)


@router.patch("/{instructor_id}/reject")
def reject_instructor(
    instructor_id: str,
    payload: RejectInstructorRequest,
    admin_user: CurrentAdmin,
    service: Annotated[AdminValidationService, Depends(get_admin_validation_service)],
    db: DbSession,
) -> Response:
    """Reject an instructor's credentials.

    Requires the ADMIN role. Marks the instructor as REJEITADO with the optional
    reason, purges the uploaded documents, notifies the instructor and returns the
    updated user. Returns 404 when the instructor does not exist.
    """
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
    db.commit()
    return success_response(result.instructor)
