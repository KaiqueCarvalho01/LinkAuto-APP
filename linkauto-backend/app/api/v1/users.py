from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict

from app.api.deps import AuthenticatedUser, get_current_user
from app.services.dependencies import get_profile_service
from app.services.profile_service import ProfileService
from app.schemas.common import success_response

router = APIRouter(prefix="/users", tags=["users"])


class UserMePatchRequest(BaseModel):
    model_config = ConfigDict(extra="allow")


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
        user_payload = profile_service.update_me(current_user.user_id, payload.model_dump())
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
