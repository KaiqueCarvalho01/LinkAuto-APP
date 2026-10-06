"""FastAPI dependency providers for the application services."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

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
    """Return the cached notification service, backed by the in-memory email gateway."""
    return NotificationService(email_gateway=InMemoryEmailGateway())


def get_store() -> IdentityStore:
    """Return the shared identity store."""
    return get_identity_store()


def get_auth_service(settings: Annotated[Settings, Depends(get_settings)]) -> AuthService:
    """Build an ``AuthService`` wired to the shared store and notification service."""
    return AuthService(
        settings=settings,
        store=get_store(),
        notification_service=get_notification_service(),
    )


def get_profile_service() -> ProfileService:
    """Build a ``ProfileService`` on the shared identity store."""
    return ProfileService(store=get_store())


def get_cleanup_service() -> DocumentCleanupService:
    """Build a ``DocumentCleanupService`` on the shared identity store."""
    return DocumentCleanupService(store=get_store())


def get_admin_validation_service() -> AdminValidationService:
    """Build an ``AdminValidationService`` with its profile, cleanup and notification services."""
    return AdminValidationService(
        store=get_store(),
        profile_service=get_profile_service(),
        cleanup_service=get_cleanup_service(),
        notification_service=get_notification_service(),
    )


def get_instructor_document_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> InstructorDocumentService:
    """Build an ``InstructorDocumentService`` on the shared identity store."""
    return InstructorDocumentService(settings=settings, store=get_store())
