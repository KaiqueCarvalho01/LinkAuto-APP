"""Credential uploads are bounded in size, count and status (#78)."""

from typing import TYPE_CHECKING, cast

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.models import InstructorProfile
from app.models.user import DetranStatus
from app.services.dependencies import get_document_storage
from app.services.document_storage import InMemoryDocumentStorage
from app.services.identity_repository import IdentityRepository
from app.services.instructor_document_service import (
    MAX_FILE_SIZE_BYTES,
    DocumentTooLargeError,
    InstructorDocumentService,
)
from tests.factories import admin_headers, auth_headers

if TYPE_CHECKING:
    from fastapi import FastAPI, UploadFile
    from sqlmodel import Session

PDF = b"%PDF-1.4\nfake credential"
PNG = b"\x89PNG\r\n\x1a\nfake record"


@pytest.fixture
def storage(client: TestClient) -> InMemoryDocumentStorage:
    memory = InMemoryDocumentStorage()
    cast("FastAPI", client.app).dependency_overrides[get_document_storage] = lambda: memory
    return memory


@pytest.fixture
def instructor(db_session: Session) -> tuple[str, dict[str, str]]:
    user = IdentityRepository(db_session).create_user("up@test.com", "h", ["INSTRUTOR"])
    db_session.commit()
    return user.id, auth_headers(user)


def _upload(client: TestClient, instructor_id: str, headers: dict[str, str]) -> int:
    return client.post(
        f"/api/v1/instructors/{instructor_id}/documents",
        files={
            "detran_credential": ("c.pdf", PDF, "application/pdf"),
            "criminal_record": ("r.png", PNG, "image/png"),
        },
        headers=headers,
    ).status_code


def test_a_new_upload_replaces_the_previous_set(
    client: TestClient,
    db_session: Session,
    storage: InMemoryDocumentStorage,
    instructor: tuple[str, dict[str, str]],
) -> None:
    instructor_id, headers = instructor
    assert _upload(client, instructor_id, headers) == 201
    first_keys = set(storage.objects)

    assert _upload(client, instructor_id, headers) == 201

    assert len(storage.objects) == 2
    assert not first_keys & set(storage.objects)
    listed = client.get(
        f"/api/v1/admin/instructors/{instructor_id}/documents",
        headers=admin_headers(db_session),
    ).json()["data"]
    assert len(listed) == 1


def test_approved_instructors_cannot_upload(
    client: TestClient,
    db_session: Session,
    storage: InMemoryDocumentStorage,
    instructor: tuple[str, dict[str, str]],
) -> None:
    instructor_id, headers = instructor
    profile = db_session.get(InstructorProfile, instructor_id)
    assert profile is not None
    profile.detran_status = DetranStatus.APROVADO
    db_session.commit()

    assert _upload(client, instructor_id, headers) == 409
    assert storage.objects == {}


def test_rejected_instructors_can_send_new_documents(
    client: TestClient,
    db_session: Session,
    storage: InMemoryDocumentStorage,
    instructor: tuple[str, dict[str, str]],
) -> None:
    instructor_id, headers = instructor
    profile = db_session.get(InstructorProfile, instructor_id)
    assert profile is not None
    profile.detran_status = DetranStatus.REJEITADO
    db_session.commit()

    assert _upload(client, instructor_id, headers) == 201
    assert len(storage.objects) == 2


def test_uploads_are_limited_per_user(
    client: TestClient,
    storage: InMemoryDocumentStorage,
    instructor: tuple[str, dict[str, str]],
) -> None:
    del storage
    instructor_id, headers = instructor

    statuses = [_upload(client, instructor_id, headers) for _ in range(11)]

    assert statuses[:10] == [201] * 10
    assert statuses[10] == 429


class _EndlessUpload:
    """An upload that never ends, counting what was read from it."""

    content_type = "application/pdf"
    filename = "huge.pdf"

    def __init__(self) -> None:
        self.read_bytes = 0

    async def read(self, size: int = -1) -> bytes:
        assert size > 0, "the upload must be read in chunks"
        self.read_bytes += size
        return b"%PDF" + b"0" * (size - 4)


@pytest.mark.anyio
async def test_oversized_files_are_not_read_whole() -> None:
    upload = _EndlessUpload()

    with pytest.raises(DocumentTooLargeError):
        await InstructorDocumentService._read_and_validate(cast("UploadFile", upload))  # noqa: SLF001

    # Stops right after passing the limit
    assert upload.read_bytes <= MAX_FILE_SIZE_BYTES + 64 * 1024


def test_request_bodies_over_the_limit_get_413() -> None:
    small = TestClient(create_app(Settings(MAX_REQUEST_BODY_BYTES=1024)))

    resp = small.post("/api/v1/auth/login", content=b"x" * 2048)

    assert resp.status_code == 413
    assert resp.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"
    # Smaller bodies go through to the app as usual
    assert small.post("/api/v1/auth/login", json={}).status_code == 422
