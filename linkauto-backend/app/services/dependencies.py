from __future__ import annotations

from functools import lru_cache

from fastapi import Depends

from app.core import Settings, get_settings
from app.services.admin_validation_service import AdminValidationService
from app.services.auth_service import AuthService
from app.services.document_cleanup_service import DocumentCleanupService
from app.services.instructor_document_service import InstructorDocumentService
from app.services.notification_service import InMemoryEmailGateway, NotificationService
from app.services.profile_service import ProfileService
from app.services.us1_store import IdentityStore, get_identity_store


@lru_cache(maxsize=1)
def get_notification_service() -> NotificationService:
    return NotificationService(email_gateway=InMemoryEmailGateway())


def get_store() -> IdentityStore:
    return get_identity_store()


def get_auth_service(settings: Settings = Depends(get_settings)) -> AuthService:
    return AuthService(
        settings=settings,
        store=get_store(),
        notification_service=get_notification_service(),
    )


def get_profile_service() -> ProfileService:
    return ProfileService(store=get_store())


def get_cleanup_service() -> DocumentCleanupService:
    return DocumentCleanupService(store=get_store())


def get_admin_validation_service() -> AdminValidationService:
    return AdminValidationService(
        store=get_store(),
        profile_service=get_profile_service(),
        cleanup_service=get_cleanup_service(),
        notification_service=get_notification_service(),
    )


def get_instructor_document_service(
    settings: Settings = Depends(get_settings),
) -> InstructorDocumentService:
    return InstructorDocumentService(settings=settings, store=get_store())
