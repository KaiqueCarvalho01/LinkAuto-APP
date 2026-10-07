"""Endpoint for uploading instructor credential documents."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status

from app.api.deps.types import CurrentUser, DbSession
from app.schemas.common import success_response
from app.services.dependencies import get_instructor_document_service
from app.services.instructor_document_service import (
    DocumentTooLargeError,
    DocumentValidationError,
    InstructorDocumentService,
)

router = APIRouter(prefix="/instructors", tags=["instructor-documents"])


@router.post("/{instructor_id}/documents")
async def upload_documents(  # noqa: PLR0913, PLR0917 - FastAPI injects each dependency
    instructor_id: str,
    detran_credential: Annotated[UploadFile, File()],
    criminal_record: Annotated[UploadFile, File()],
    current_user: CurrentUser,
    service: Annotated[InstructorDocumentService, Depends(get_instructor_document_service)],
    db: DbSession,
) -> Response:
    """Upload an instructor's DETRAN credential and criminal record documents.

    May be called by the instructor themself or by an ADMIN; any other caller gets
    403. Each file must be a PDF, JPEG or PNG whose content matches its declared type
    (400 otherwise) and at most 10 MB (413 otherwise). Returns 404 when the instructor
    does not exist.
    """
    if current_user.user_id != instructor_id and "ADMIN" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Cannot upload documents for another instructor.",
            },
        )
    try:
        result = await service.upload_documents(
            instructor_id=instructor_id,
            detran_credential=detran_credential,
            criminal_record=criminal_record,
        )
    except DocumentValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": str(exc)},
        ) from exc
    except DocumentTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail={"code": "PAYLOAD_TOO_LARGE", "message": str(exc)},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
    db.commit()
    return success_response(
        {
            "instructor_id": result.instructor_id,
            "document_id": result.document_id,
            "detran_credential_url": result.detran_credential_url,
            "criminal_record_url": result.criminal_record_url,
        },
        status_code=status.HTTP_201_CREATED,
    )
