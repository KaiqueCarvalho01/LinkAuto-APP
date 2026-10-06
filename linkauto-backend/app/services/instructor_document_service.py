"""Validation and registration of instructor credential documents (DETRAN, criminal record)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import UploadFile

    from app.core import Settings
    from app.services.us1_store import IdentityStore

ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

MAGIC_BYTES = {
    "application/pdf": [b"%PDF"],
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
}


class DocumentValidationError(ValueError):
    """Raised when a file's MIME type is not allowed or its content does not match it."""


class DocumentTooLargeError(ValueError):
    """Raised when an uploaded file exceeds the 10 MB limit."""


@dataclass
class UploadedInstructorDocuments:
    """Stored document record for an instructor, with the object URLs of both files."""

    instructor_id: str
    document_id: str
    detran_credential_url: str
    criminal_record_url: str


class InstructorDocumentService:
    """Validate instructor credential uploads and record them for admin review."""

    def __init__(self, *, settings: Settings, store: IdentityStore) -> None:
        """Store the settings (for the S3 bucket name) and the identity store."""
        self._settings = settings
        self._store = store

    @staticmethod
    async def _read_and_validate(upload: UploadFile) -> bytes:
        if upload.content_type not in ALLOWED_MIME_TYPES:
            msg = (
                f"Unsupported MIME type '{upload.content_type}'. Allowed: "
                f"{', '.join(sorted(ALLOWED_MIME_TYPES))}."
            )
            raise DocumentValidationError(msg)

        content = await upload.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            msg = "File exceeds 10MB limit."
            raise DocumentTooLargeError(msg)

        # D06: Validar Magic Bytes para evitar MIME spoofing
        mime = upload.content_type
        if mime in MAGIC_BYTES:
            signatures = MAGIC_BYTES[mime]
            matched = any(content.startswith(sig) for sig in signatures)
            if not matched:
                msg = (
                    "INVALID_FILE_CONTENT: File content does not match declared MIME type '"
                    f"{mime}'."
                )
                raise DocumentValidationError(msg)

        return content

    def _build_object_url(self, instructor_id: str, filename: str) -> str:
        safe_name = Path(filename).name
        bucket = self._settings.s3_bucket or "local-bucket"
        return f"s3://{bucket}/instructors/{instructor_id}/{safe_name}"

    async def upload_documents(
        self, *, instructor_id: str, detran_credential: UploadFile, criminal_record: UploadFile
    ) -> UploadedInstructorDocuments:
        """Validate both files and register a document record with their S3 object URLs.

        Each file must be a PDF, JPEG or PNG of at most 10 MB whose magic bytes match the
        declared MIME type. Only the URLs are stored; the file content is not uploaded here.
        Raises ``DocumentValidationError`` or ``DocumentTooLargeError`` on invalid files.
        """
        await self._read_and_validate(detran_credential)
        await self._read_and_validate(criminal_record)

        record = self._store.add_instructor_document(
            instructor_id,
            detran_credential_url=self._build_object_url(
                instructor_id, detran_credential.filename or "detran"
            ),
            criminal_record_url=self._build_object_url(
                instructor_id, criminal_record.filename or "criminal"
            ),
        )

        return UploadedInstructorDocuments(
            instructor_id=instructor_id,
            document_id=record.id,
            detran_credential_url=record.detran_credential_url,
            criminal_record_url=record.criminal_record_url,
        )
