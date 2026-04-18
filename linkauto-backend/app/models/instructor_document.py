from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.models.base import AuditUUIDBase


class InstructorDocument(AuditUUIDBase):
    __tablename__ = "instructor_documents"

    instructor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("instructor_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    reviewed_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    detran_credential_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    criminal_record_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDENTE")
    review_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)


class InstructorDocumentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, document: InstructorDocument) -> InstructorDocument:
        self._session.add(document)
        self._session.flush()
        return document

    def list_by_instructor(self, instructor_id: str) -> list[InstructorDocument]:
        statement = (
            select(InstructorDocument)
            .where(InstructorDocument.instructor_id == instructor_id)
            .order_by(InstructorDocument.uploaded_at.desc())
        )
        return list(self._session.scalars(statement))

    def mark_reviewed(
        self,
        instructor_id: str,
        *,
        reviewed_by: str,
        reviewed_at: datetime,
        status: str,
        reason: str | None,
    ) -> list[InstructorDocument]:
        documents = self.list_by_instructor(instructor_id)
        for document in documents:
            document.reviewed_by = reviewed_by
            document.reviewed_at = reviewed_at
            document.review_status = status
            document.review_reason = reason
        self._session.flush()
        return documents
