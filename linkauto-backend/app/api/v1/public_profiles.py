from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import success_response
from app.services.public_profile_service import PublicProfileService

router = APIRouter(tags=["public-profiles"])


@router.get("/instructors/{instructor_id}/public")
def get_public_instructor_profile(
    instructor_id: str,
    db: Session = Depends(get_db),
) -> Response:
    service = PublicProfileService(db)
    try:
        profile = service.get_public_instructor(instructor_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
    return success_response(profile.model_dump())


@router.get("/students/{student_id}/public")
def get_public_student_profile(
    student_id: str,
    db: Session = Depends(get_db),
) -> Response:
    service = PublicProfileService(db)
    try:
        profile = service.get_public_student(student_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
    return success_response(profile.model_dump())
