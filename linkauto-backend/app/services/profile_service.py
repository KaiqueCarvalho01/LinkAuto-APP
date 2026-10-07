"""Read and update the authenticated user's profile and list approved instructors."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.schemas.public_profile import PublicInstructorSummary
from app.services.identity_repository import (
    UserNotFoundError,
    serialize_instructor_profile,
    serialize_student_profile,
)

if TYPE_CHECKING:
    from app.models import User
    from app.services.identity_repository import IdentityRepository


def serialize_user(user: User) -> dict[str, Any]:
    """Return the private (owner/admin) view of a user account and its profiles."""
    return {
        "id": user.id,
        "email": user.email,
        "roles": list(user.roles),
        "is_active": user.is_active,
        "student_profile": serialize_student_profile(user.student_profile)
        if user.student_profile
        else None,
        "instructor_profile": serialize_instructor_profile(user.instructor_profile)
        if user.instructor_profile
        else None,
        "created_at": user.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": user.updated_at.isoformat().replace("+00:00", "Z"),
    }


class ProfileService:
    """Serialize user profiles from the identity repository into API payloads."""

    def __init__(self, repository: IdentityRepository) -> None:
        """Store the repository used to look up and update users."""
        self._repository = repository

    def get_me(self, user_id: str) -> dict[str, Any]:
        """Return the serialized user; raise ``UserNotFoundError`` if it does not exist."""
        user = self._repository.get_user(user_id)
        if user is None:
            msg = "User not found."
            raise UserNotFoundError(msg)
        return serialize_user(user)

    def update_me(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Merge the student/instructor profile updates in ``payload`` and return the user.

        Raises ``ValueError`` if the user is missing or lacks the matching role.
        """
        return serialize_user(self._repository.update_profile(user_id, payload))

    def list_public_instructors(self) -> list[dict[str, Any]]:
        """Return the public cards of active, DETRAN-approved instructors, keyed by slug.

        Only public-safe fields: no user ID, email, phone or internal status.
        """
        return [
            PublicInstructorSummary(
                id=slug,
                slug=slug,
                full_name=profile.full_name,
                avatar_url=profile.avatar_url,
                city=profile.city,
                state=profile.state,
                bio=profile.bio,
                specialties=list(profile.specialties or []),
                price_per_hour=float(profile.price_per_hour)
                if profile.price_per_hour is not None
                else None,
                rating_avg=profile.rating_avg,
                rating_count=profile.rating_count,
                latitude=profile.latitude,
                longitude=profile.longitude,
                action_radius_km=profile.action_radius_km,
            ).model_dump()
            for profile in self._repository.list_public_instructors()
            for slug in [self._repository.ensure_instructor_slug(profile)]
        ]
