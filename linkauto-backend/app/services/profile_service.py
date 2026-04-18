from __future__ import annotations

from app.models import DetranStatus
from app.services.us1_store import IdentityStore, UserRecord


class ProfileService:
    def __init__(self, store: IdentityStore) -> None:
        self._store = store

    @staticmethod
    def _serialize_user(user: UserRecord) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "roles": user.roles,
            "is_active": user.is_active,
            "student_profile": user.student_profile,
            "instructor_profile": user.instructor_profile,
            "created_at": user.created_at.isoformat().replace("+00:00", "Z"),
            "updated_at": user.updated_at.isoformat().replace("+00:00", "Z"),
        }

    def get_me(self, user_id: str) -> dict:
        user = self._store.get_user(user_id)
        if user is None:
            raise ValueError("User not found.")
        return self._serialize_user(user)

    def update_me(self, user_id: str, payload: dict) -> dict:
        user = self._store.update_profile(user_id, payload)
        return self._serialize_user(user)

    def list_public_instructors(self) -> list[dict]:
        instructors = self._store.list_public_instructors()
        response: list[dict] = []
        for user in instructors:
            if not user.instructor_profile:
                continue
            if user.instructor_profile.get("detran_status") != DetranStatus.APROVADO.value:
                continue
            response.append(
                {
                    "id": user.id,
                    "email": user.email,
                    "instructor_profile": user.instructor_profile,
                }
            )
        return response
