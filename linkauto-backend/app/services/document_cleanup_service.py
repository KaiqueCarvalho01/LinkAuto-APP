"""Removal of instructor credential documents once an admin has reviewed them."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.document_storage import DocumentStorage
    from app.services.identity_repository import IdentityRepository


@dataclass
class DocumentCleanupResult:
    """Object keys of the documents purged for an instructor and how many there were."""

    instructor_id: str
    purged_keys: list[str]
    purged_count: int


class DocumentCleanupService:
    """Purge stored instructor documents after the DETRAN validation decision."""

    def __init__(self, repository: IdentityRepository, storage: DocumentStorage) -> None:
        """Store the repository holding the document records and the object storage."""
        self._repository = repository
        self._storage = storage

    def purge_after_validation(self, instructor_id: str) -> DocumentCleanupResult:
        """Delete the instructor's document records and stored files (LGPD retention)."""
        purged_keys = self._repository.purge_instructor_documents(instructor_id)
        self._storage.delete(purged_keys)
        return DocumentCleanupResult(
            instructor_id=instructor_id,
            purged_keys=purged_keys,
            purged_count=len(purged_keys),
        )
