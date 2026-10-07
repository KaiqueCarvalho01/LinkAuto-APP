"""Endpoints for the current user's account and profiles."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict

from app.api.deps.types import CurrentUser, DbSession
from app.schemas.common import success_response
from app.services.dependencies import get_profile_service
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/users", tags=["users"])


class StudentProfilePatch(BaseModel):
    """Partial update of the student profile; unknown fields are rejected."""

    model_config = ConfigDict(extra="forbid")
    full_name: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
    license_type: str | None = None
    avatar_url: str | None = None


class InstructorProfilePatch(BaseModel):
    """Partial update of the instructor profile; unknown fields are rejected."""

    model_config = ConfigDict(extra="forbid")
    full_name: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
    bio: str | None = None
    specialties: list[str] | None = None
    price_per_hour: float | None = None
    avatar_url: str | None = None
    action_radius_km: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_active: bool | None = None


class UserMePatchRequest(BaseModel):
    """Partial update of the current user's student and/or instructor profile."""

    model_config = ConfigDict(extra="forbid")
    student_profile: StudentProfilePatch | None = None
    instructor_profile: InstructorProfilePatch | None = None


@router.get("/me")
def get_me(
    current_user: CurrentUser,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> Response:
    """Return the current user's account and profiles.

    Requires authentication. Returns 404 when the user no longer exists.
    """
    try:
        payload = profile_service.get_me(current_user.user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(exc)},
        ) from exc
    return success_response(payload)


@router.patch("/me")
def patch_me(
    payload: UserMePatchRequest,
    current_user: CurrentUser,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
    db: DbSession,
) -> Response:
    """Update the current user's student and/or instructor profile.

    Requires authentication. Only provided fields are changed. Returns 400 when the
    user lacks the role matching a submitted profile or does not exist.
    """
    try:
        user_payload = profile_service.update_me(
            current_user.user_id, payload.model_dump(exclude_unset=True)
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": str(exc)},
        ) from exc
    db.commit()
    return success_response(user_payload)


@router.get("/public-instructors")
def list_public_instructors(
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> Response:
    """List instructors whose credentials have been approved.

    Public.
    """
    return success_response(profile_service.list_public_instructors())
