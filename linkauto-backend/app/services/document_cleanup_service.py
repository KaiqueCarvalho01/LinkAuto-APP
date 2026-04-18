from __future__ import annotations

from dataclasses import dataclass

from app.services.us1_store import IdentityStore


@dataclass
class DocumentCleanupResult:
    instructor_id: str
    purged_keys: list[str]
    purged_count: int


class DocumentCleanupService:
    def __init__(self, store: IdentityStore) -> None:
        self._store = store

    def purge_after_validation(self, instructor_id: str) -> DocumentCleanupResult:
        purged_keys = self._store.purge_instructor_documents(instructor_id)
        return DocumentCleanupResult(
            instructor_id=instructor_id,
            purged_keys=purged_keys,
            purged_count=len(purged_keys),
        )
