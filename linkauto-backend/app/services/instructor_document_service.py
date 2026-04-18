from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile

from app.core import Settings
from app.services.us1_store import IdentityStore

ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


class DocumentValidationError(ValueError):
    pass


class DocumentTooLargeError(ValueError):
    pass


@dataclass
class UploadedInstructorDocuments:
    instructor_id: str
    document_id: str
    detran_credential_url: str
    criminal_record_url: str


class InstructorDocumentService:
    def __init__(self, *, settings: Settings, store: IdentityStore) -> None:
        self._settings = settings
        self._store = store

    @staticmethod
    async def _read_and_validate(upload: UploadFile) -> bytes:
        if upload.content_type not in ALLOWED_MIME_TYPES:
            raise DocumentValidationError(
                f"Unsupported MIME type '{upload.content_type}'. Allowed: {', '.join(sorted(ALLOWED_MIME_TYPES))}."
            )

        content = await upload.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise DocumentTooLargeError("File exceeds 10MB limit.")
        return content

    def _build_object_url(self, instructor_id: str, filename: str) -> str:
        safe_name = Path(filename).name
        bucket = self._settings.s3_bucket or "local-bucket"
        return f"s3://{bucket}/instructors/{instructor_id}/{safe_name}"

    async def upload_documents(
        self, *, instructor_id: str, detran_credential: UploadFile, criminal_record: UploadFile
    ) -> UploadedInstructorDocuments:
        await self._read_and_validate(detran_credential)
        await self._read_and_validate(criminal_record)

        record = self._store.add_instructor_document(
            instructor_id,
            detran_credential_url=self._build_object_url(instructor_id, detran_credential.filename or "detran"),
            criminal_record_url=self._build_object_url(instructor_id, criminal_record.filename or "criminal"),
        )

        return UploadedInstructorDocuments(
            instructor_id=instructor_id,
            document_id=record.id,
            detran_credential_url=record.detran_credential_url,
            criminal_record_url=record.criminal_record_url,
        )
