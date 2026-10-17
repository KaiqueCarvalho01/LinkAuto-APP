"""Admin review of instructor credentials (DETRAN approval or rejection)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from app.core import get_settings
from app.models import DetranStatus
from app.services.booking_notifier import INSTRUCTOR_FALLBACK_NAME
from app.services.notification_templates import NO_REASON, EmailTemplateName, render_email
from app.services.profile_service import serialize_user

if TYPE_CHECKING:
    from app.services.document_cleanup_service import DocumentCleanupResult, DocumentCleanupService
    from app.services.identity_repository import IdentityRepository
    from app.services.notification_service import NotificationService
    from app.services.profile_service import ProfileService


@dataclass
class AdminValidationResult:
    """Outcome of an admin decision: the updated instructor payload and the document purge."""

    instructor: dict[str, Any]
    cleanup: DocumentCleanupResult


class AdminValidationService:
    """List instructors for review and approve or reject their DETRAN credentials."""

    def __init__(
        self,
        *,
        repository: IdentityRepository,
        profile_service: ProfileService,
        cleanup_service: DocumentCleanupService,
        notification_service: NotificationService | None = None,
    ) -> None:
        """Wire the collaborators; without a notification service no e-mail is sent."""
        self._repository = repository
        self._profile_service = profile_service
        self._cleanup_service = cleanup_service
        self._notification_service = notification_service

    def list_instructors(
        self, *, status: str | None = None, page: int = 1, page_size: int = 20
    ) -> dict[str, Any]:
        """Return a page of instructor accounts, optionally filtered by DETRAN status."""
        result = self._repository.list_instructors(status=status, page=page, page_size=page_size)
        return {
            "items": [serialize_user(user) for user in result.items],
            "total": result.total,
            "page": page,
            "page_size": page_size,
        }

    def approve(self, *, instructor_id: str, admin_id: str) -> AdminValidationResult:
        """Set the instructor's DETRAN status to APROVADO, required for public visibility.

        Also purges the submitted documents and notifies the instructor by e-mail.
        """
        self._repository.review_instructor(
            instructor_id,
            status=DetranStatus.APROVADO.value,
            reviewed_by=admin_id,
            reason=None,
        )
        cleanup = self._cleanup_service.purge_after_validation(instructor_id)
        instructor_payload = self._profile_service.get_me(instructor_id)
        self._dispatch_validation_notification(instructor_payload, approved=True, reason=None)
        return AdminValidationResult(instructor=instructor_payload, cleanup=cleanup)

    def reject(
        self, *, instructor_id: str, admin_id: str, reason: str | None
    ) -> AdminValidationResult:
        """Set the instructor's DETRAN status to REJEITADO with an optional reason.

        Also purges the submitted documents and e-mails the instructor the reason.
        """
        self._repository.review_instructor(
            instructor_id,
            status=DetranStatus.REJEITADO.value,
            reviewed_by=admin_id,
            reason=reason,
        )
        cleanup = self._cleanup_service.purge_after_validation(instructor_id)
        instructor_payload = self._profile_service.get_me(instructor_id)
        self._dispatch_validation_notification(instructor_payload, approved=False, reason=reason)
        return AdminValidationResult(instructor=instructor_payload, cleanup=cleanup)

    def _dispatch_validation_notification(
        self, instructor: dict[str, Any], *, approved: bool, reason: str | None
    ) -> None:
        if self._notification_service is None:
            return
        profile = instructor.get("instructor_profile") or {}
        values = {
            "recipient_name": profile.get("full_name") or INSTRUCTOR_FALLBACK_NAME,
            "link": get_settings().frontend_link("/profile"),
        }
        if approved:
            template = EmailTemplateName.INSTRUCTOR_APPROVED
        else:
            template = EmailTemplateName.INSTRUCTOR_REJECTED
            values["reason"] = reason or NO_REASON
        self._notification_service.dispatch(render_email(template, [instructor["email"]], **values))
