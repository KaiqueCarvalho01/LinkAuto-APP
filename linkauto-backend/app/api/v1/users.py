from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict

from app.api.deps import AuthenticatedUser, get_current_user
from app.services.dependencies import get_profile_service
from app.services.profile_service import ProfileService
from app.schemas.common import success_response

router = APIRouter(prefix="/users", tags=["users"])


class StudentProfilePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str | None = None
    phone: str | None = None
    city: str | None = None
    state: str | None = None
    license_type: str | None = None
    avatar_url: str | None = None


class InstructorProfilePatch(BaseModel):
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
    model_config = ConfigDict(extra="forbid")
    student_profile: StudentProfilePatch | None = None
    instructor_profile: InstructorProfilePatch | None = None


@router.get("/me")
def get_me(
    current_user: AuthenticatedUser = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> Response:
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
    current_user: AuthenticatedUser = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> Response:
    try:
        user_payload = profile_service.update_me(
            current_user.user_id, 
            payload.model_dump(exclude_unset=True)
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": str(exc)},
        ) from exc
    return success_response(user_payload)


@router.get("/public-instructors")
def list_public_instructors(
    profile_service: ProfileService = Depends(get_profile_service),
) -> Response:
    return success_response(profile_service.list_public_instructors())
