"""FastAPI dependency providers for the application services."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.api.deps.types import DbSession  # noqa: TC001 - FastAPI resolves it at runtime
from app.core import Settings, get_settings
from app.services.admin_validation_service import AdminValidationService
from app.services.auth_service import AuthService
from app.services.document_cleanup_service import DocumentCleanupService
from app.services.identity_repository import IdentityRepository
from app.services.instructor_document_service import InstructorDocumentService
from app.services.notification_service import InMemoryEmailGateway, NotificationService
from app.services.profile_service import ProfileService
from app.services.refresh_token_repository import RefreshTokenRepository


@lru_cache(maxsize=1)
def get_notification_service() -> NotificationService:
    """Return the cached notification service, backed by the in-memory email gateway."""
    return NotificationService(email_gateway=InMemoryEmailGateway())


def get_identity_repository(db: DbSession) -> IdentityRepository:
    """Return an identity repository bound to the request's database session."""
    return IdentityRepository(db)


Repository = Annotated[IdentityRepository, Depends(get_identity_repository)]


def get_auth_service(
    settings: Annotated[Settings, Depends(get_settings)], repository: Repository, db: DbSession
) -> AuthService:
    """Build an ``AuthService`` wired to the request's repositories and notifications."""
    return AuthService(
        settings=settings,
        repository=repository,
        refresh_tokens=RefreshTokenRepository(db),
        notification_service=get_notification_service(),
    )


def get_profile_service(repository: Repository) -> ProfileService:
    """Build a ``ProfileService`` on the request's identity repository."""
    return ProfileService(repository)


def get_cleanup_service(repository: Repository) -> DocumentCleanupService:
    """Build a ``DocumentCleanupService`` on the request's identity repository."""
    return DocumentCleanupService(repository)


def get_admin_validation_service(repository: Repository) -> AdminValidationService:
    """Build an ``AdminValidationService`` with its profile, cleanup and notification services."""
    return AdminValidationService(
        repository=repository,
        profile_service=ProfileService(repository),
        cleanup_service=DocumentCleanupService(repository),
        notification_service=get_notification_service(),
    )


def get_instructor_document_service(
    settings: Annotated[Settings, Depends(get_settings)], repository: Repository
) -> InstructorDocumentService:
    """Build an ``InstructorDocumentService`` on the request's identity repository."""
    return InstructorDocumentService(settings=settings, repository=repository)
