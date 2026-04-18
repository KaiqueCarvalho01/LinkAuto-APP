from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock

from app.models import DetranStatus, LicenseType, UserRole, generate_uuid7
from app.models.base import utc_now


ALLOWED_ROLES = {role.value for role in UserRole}


@dataclass
class UserRecord:
    id: str
    email: str
    password_hash: str
    roles: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    student_profile: dict | None = None
    instructor_profile: dict | None = None


@dataclass
class InstructorDocumentRecord:
    id: str
    instructor_id: str
    detran_credential_url: str
    criminal_record_url: str
    uploaded_at: datetime
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None
    review_status: str = DetranStatus.PENDENTE.value
    review_reason: str | None = None


@dataclass
class IdentityStore:
    _lock: Lock = field(default_factory=Lock)
    _users: dict[str, UserRecord] = field(default_factory=dict)
    _email_to_id: dict[str, str] = field(default_factory=dict)
    _documents: dict[str, InstructorDocumentRecord] = field(default_factory=dict)
    _documents_by_instructor: dict[str, list[str]] = field(default_factory=dict)

    def reset(self) -> None:
        with self._lock:
            self._users.clear()
            self._email_to_id.clear()
            self._documents.clear()
            self._documents_by_instructor.clear()

    def create_user(self, email: str, password_hash: str, roles: Iterable[str]) -> UserRecord:
        normalized_email = email.strip().lower()
        role_list = sorted(set(roles))
        if not role_list:
            raise ValueError("At least one role is required.")
        invalid_roles = sorted(set(role_list) - ALLOWED_ROLES)
        if invalid_roles:
            raise ValueError(f"Unsupported role(s): {', '.join(invalid_roles)}")

        with self._lock:
            if normalized_email in self._email_to_id:
                raise ValueError("Email already registered.")

            now = utc_now()
            user = UserRecord(
                id=generate_uuid7(),
                email=normalized_email,
                password_hash=password_hash,
                roles=role_list,
                is_active=True,
                created_at=now,
                updated_at=now,
                student_profile=self._default_student_profile() if UserRole.ALUNO.value in role_list else None,
                instructor_profile=self._default_instructor_profile()
                if UserRole.INSTRUTOR.value in role_list
                else None,
            )
            self._users[user.id] = user
            self._email_to_id[normalized_email] = user.id
            return user

    @staticmethod
    def _default_student_profile() -> dict:
        return {
            "full_name": None,
            "phone": None,
            "city": None,
            "state": None,
            "license_type": LicenseType.NENHUMA.value,
            "avatar_url": None,
        }

    @staticmethod
    def _default_instructor_profile() -> dict:
        return {
            "full_name": None,
            "phone": None,
            "city": None,
            "state": None,
            "bio": None,
            "specialties": [],
            "price_per_hour": None,
            "avatar_url": None,
            "detran_status": DetranStatus.PENDENTE.value,
            "action_radius_km": 10,
            "latitude": None,
            "longitude": None,
            "rating_avg": 0.0,
            "rating_count": 0,
            "is_active": True,
        }

    def get_user_by_email(self, email: str) -> UserRecord | None:
        user_id = self._email_to_id.get(email.strip().lower())
        if not user_id:
            return None
        return self._users.get(user_id)

    def get_user(self, user_id: str) -> UserRecord | None:
        return self._users.get(user_id)

    def update_profile(self, user_id: str, payload: dict) -> UserRecord:
        user = self.get_user(user_id)
        if user is None:
            raise ValueError("User not found.")

        student_update = payload.get("student_profile")
        instructor_update = payload.get("instructor_profile")

        if student_update is not None:
            if UserRole.ALUNO.value not in user.roles:
                raise ValueError("User does not have ALUNO role.")
            if user.student_profile is None:
                user.student_profile = self._default_student_profile()
            user.student_profile.update(student_update)

        if instructor_update is not None:
            if UserRole.INSTRUTOR.value not in user.roles:
                raise ValueError("User does not have INSTRUTOR role.")
            if user.instructor_profile is None:
                user.instructor_profile = self._default_instructor_profile()
            user.instructor_profile.update(instructor_update)

        user.updated_at = utc_now()
        return user

    def list_instructors(self, *, status: str | None = None) -> list[UserRecord]:
        instructors: list[UserRecord] = []
        for user in self._users.values():
            profile = user.instructor_profile
            if profile is None:
                continue
            if status and profile.get("detran_status") != status:
                continue
            instructors.append(user)
        return instructors

    def list_public_instructors(self) -> list[UserRecord]:
        return [
            instructor
            for instructor in self.list_instructors(status=DetranStatus.APROVADO.value)
            if instructor.instructor_profile and instructor.instructor_profile.get("is_active", True)
        ]

    def add_instructor_document(
        self, instructor_id: str, *, detran_credential_url: str, criminal_record_url: str
    ) -> InstructorDocumentRecord:
        instructor = self.get_user(instructor_id)
        if instructor is None or instructor.instructor_profile is None:
            raise ValueError("Instructor not found.")

        document = InstructorDocumentRecord(
            id=generate_uuid7(),
            instructor_id=instructor_id,
            detran_credential_url=detran_credential_url,
            criminal_record_url=criminal_record_url,
            uploaded_at=utc_now(),
        )
        self._documents[document.id] = document
        self._documents_by_instructor.setdefault(instructor_id, []).append(document.id)
        return document

    def list_documents(self, instructor_id: str) -> list[InstructorDocumentRecord]:
        document_ids = self._documents_by_instructor.get(instructor_id, [])
        return [self._documents[doc_id] for doc_id in document_ids if doc_id in self._documents]

    def review_instructor(
        self, instructor_id: str, *, status: str, reviewed_by: str, reason: str | None = None
    ) -> UserRecord:
        instructor = self.get_user(instructor_id)
        if instructor is None or instructor.instructor_profile is None:
            raise ValueError("Instructor not found.")

        instructor.instructor_profile["detran_status"] = status
        instructor.updated_at = utc_now()
        review_at = utc_now()
        for document in self.list_documents(instructor_id):
            document.reviewed_by = reviewed_by
            document.reviewed_at = review_at
            document.review_status = status
            document.review_reason = reason
        return instructor

    def purge_instructor_documents(self, instructor_id: str) -> list[str]:
        purged_keys: list[str] = []
        document_ids = self._documents_by_instructor.get(instructor_id, [])
        for doc_id in list(document_ids):
            document = self._documents.pop(doc_id, None)
            if document is None:
                continue
            purged_keys.extend([document.detran_credential_url, document.criminal_record_url])
        self._documents_by_instructor[instructor_id] = []
        return purged_keys


_identity_store = IdentityStore()


def get_identity_store() -> IdentityStore:
    return _identity_store
