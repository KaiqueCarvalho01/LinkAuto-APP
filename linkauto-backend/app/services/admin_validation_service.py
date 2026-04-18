from __future__ import annotations

from dataclasses import dataclass

from app.models import DetranStatus
from app.services.document_cleanup_service import DocumentCleanupResult, DocumentCleanupService
from app.services.notification_service import NotificationEvent, NotificationPayload, NotificationService
from app.services.profile_service import ProfileService
from app.services.us1_store import IdentityStore


@dataclass
class AdminValidationResult:
    instructor: dict
    cleanup: DocumentCleanupResult


class AdminValidationService:
    def __init__(
        self,
        *,
        store: IdentityStore,
        profile_service: ProfileService,
        cleanup_service: DocumentCleanupService,
        notification_service: NotificationService | None = None,
    ) -> None:
        self._store = store
        self._profile_service = profile_service
        self._cleanup_service = cleanup_service
        self._notification_service = notification_service

    def list_instructors(self, *, status: str | None = None, page: int = 1, page_size: int = 20) -> dict:
        instructors = self._store.list_instructors(status=status)
        start = (page - 1) * page_size
        end = start + page_size
        items = [self._profile_service.get_me(instructor.id) for instructor in instructors[start:end]]
        return {"items": items, "total": len(instructors), "page": page, "page_size": page_size}

    def approve(self, *, instructor_id: str, admin_id: str) -> AdminValidationResult:
        self._store.review_instructor(
            instructor_id,
            status=DetranStatus.APROVADO.value,
            reviewed_by=admin_id,
            reason=None,
        )
        cleanup = self._cleanup_service.purge_after_validation(instructor_id)
        instructor_payload = self._profile_service.get_me(instructor_id)
        self._dispatch_validation_notification(instructor_payload["email"], approved=True, reason=None)
        return AdminValidationResult(instructor=instructor_payload, cleanup=cleanup)

    def reject(self, *, instructor_id: str, admin_id: str, reason: str | None) -> AdminValidationResult:
        self._store.review_instructor(
            instructor_id,
            status=DetranStatus.REJEITADO.value,
            reviewed_by=admin_id,
            reason=reason,
        )
        cleanup = self._cleanup_service.purge_after_validation(instructor_id)
        instructor_payload = self._profile_service.get_me(instructor_id)
        self._dispatch_validation_notification(
            instructor_payload["email"], approved=False, reason=reason
        )
        return AdminValidationResult(instructor=instructor_payload, cleanup=cleanup)

    def _dispatch_validation_notification(
        self, recipient_email: str, *, approved: bool, reason: str | None
    ) -> None:
        if self._notification_service is None:
            return
        status_label = "aprovado" if approved else "rejeitado"
        body = (
            f"Seu credenciamento foi {status_label}."
            if approved
            else f"Seu credenciamento foi rejeitado. Motivo: {reason or 'não informado'}."
        )
        self._notification_service.dispatch(
            NotificationPayload(
                event=NotificationEvent.INSTRUCTOR_VALIDATION_DECISION,
                subject="Resultado da validação de credenciamento",
                body=body,
                recipients=[recipient_email],
            )
        )
