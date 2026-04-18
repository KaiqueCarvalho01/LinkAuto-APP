from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import AuthenticatedUser, get_current_user
from app.services.dependencies import get_instructor_document_service
from app.services.instructor_document_service import (
    DocumentTooLargeError,
    DocumentValidationError,
    InstructorDocumentService,
)
from app.schemas.common import success_response

router = APIRouter(prefix="/instructors", tags=["instructor-documents"])


@router.post("/{instructor_id}/documents")
async def upload_documents(
    instructor_id: str,
    detran_credential: UploadFile = File(...),
    criminal_record: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
    service: InstructorDocumentService = Depends(get_instructor_document_service),
):
    if current_user.user_id != instructor_id and "ADMIN" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Cannot upload documents for another instructor."},
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
    return success_response(
        {
            "instructor_id": result.instructor_id,
            "document_id": result.document_id,
            "detran_credential_url": result.detran_credential_url,
            "criminal_record_url": result.criminal_record_url,
        },
        status_code=status.HTTP_201_CREATED,
    )
