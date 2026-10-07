"""Removal of instructor credential documents once an admin has reviewed them."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.identity_repository import IdentityRepository


@dataclass
class DocumentCleanupResult:
    """Object keys of the documents purged for an instructor and how many there were."""

    instructor_id: str
    purged_keys: list[str]
    purged_count: int


class DocumentCleanupService:
    """Purge stored instructor documents after the DETRAN validation decision."""

    def __init__(self, repository: IdentityRepository) -> None:
        """Store the identity repository that holds the instructor documents."""
        self._repository = repository

    def purge_after_validation(self, instructor_id: str) -> DocumentCleanupResult:
        """Delete all document records of the instructor and return the purged object keys."""
        purged_keys = self._repository.purge_instructor_documents(instructor_id)
        return DocumentCleanupResult(
            instructor_id=instructor_id,
            purged_keys=purged_keys,
            purged_count=len(purged_keys),
        )
