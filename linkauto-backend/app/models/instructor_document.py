"""Instructor verification documents model and its repository."""

from datetime import datetime

from sqlalchemy import String
from sqlmodel import Field, Session, select

from app.models.base import AuditUUIDBase


class InstructorDocument(AuditUUIDBase, table=True):
    """Uploaded DETRAN credential and criminal record of an instructor.

    Tracks the admin review: reviewer, review time, ``review_status`` (default PENDENTE)
    and optional reason.
    """

    __tablename__ = "instructor_documents"

    instructor_id: str = Field(
        sa_type=String(36),
        foreign_key="instructor_profiles.user_id",
        ondelete="CASCADE",
        index=True,
    )
    reviewed_by: str | None = Field(
        default=None, sa_type=String(36), foreign_key="users.id", ondelete="SET NULL"
    )
    detran_credential_url: str | None = Field(default=None, sa_type=String(500))
    criminal_record_url: str | None = Field(default=None, sa_type=String(500))
    uploaded_at: datetime
    reviewed_at: datetime | None = None
    review_status: str = Field(default="PENDENTE", sa_type=String(20))
    review_reason: str | None = Field(default=None, sa_type=String(500))


class InstructorDocumentRepository:
    """Data access for InstructorDocument rows within a SQLAlchemy session."""

    def __init__(self, session: Session) -> None:
        """Bind the repository to a session."""
        self._session = session

    def add(self, document: InstructorDocument) -> InstructorDocument:
        """Add the document to the session, flush it and return it."""
        self._session.add(document)
        self._session.flush()
        return document

    def list_by_instructor(self, instructor_id: str) -> list[InstructorDocument]:
        """Return the instructor's documents, most recently uploaded first."""
        statement = (
            select(InstructorDocument)
            .where(InstructorDocument.instructor_id == instructor_id)
            .order_by(InstructorDocument.uploaded_at.desc())
        )
        return list(self._session.exec(statement))

    def mark_reviewed(
        self,
        instructor_id: str,
        *,
        reviewed_by: str,
        reviewed_at: datetime,
        status: str,
        reason: str | None,
    ) -> list[InstructorDocument]:
        """Record the review outcome on all of the instructor's documents and return them."""
        documents = self.list_by_instructor(instructor_id)
        for document in documents:
            document.reviewed_by = reviewed_by
            document.reviewed_at = reviewed_at
            document.review_status = status
            document.review_reason = reason
        self._session.flush()
        return documents
