"""Validated instructor documents are stored, viewable by admins and deleted on review (#23)."""

from typing import TYPE_CHECKING

import pytest
from sqlmodel import col, select

from app.models import InstructorDocument
from app.services.dependencies import get_document_storage
from app.services.document_storage import InMemoryDocumentStorage, LocalDocumentStorage
from app.services.identity_repository import IdentityRepository
from tests.factories import admin_headers, auth_headers

if TYPE_CHECKING:
    from pathlib import Path

    from fastapi.testclient import TestClient
    from sqlmodel import Session

PDF = b"%PDF-1.4\nfake credential"
PNG = b"\x89PNG\r\n\x1a\nfake record"


@pytest.fixture(autouse=True)
def storage(client: TestClient) -> InMemoryDocumentStorage:
    memory = InMemoryDocumentStorage()
    client.app.dependency_overrides[get_document_storage] = lambda: memory  # ty: ignore[unresolved-attribute]
    return memory


def _instructor_headers(db_session: Session) -> tuple[str, dict[str, str]]:
    user = IdentityRepository(db_session).create_user("docs@x.com", "h", ["INSTRUTOR"])
    db_session.commit()
    return user.id, auth_headers(user)


def _upload(
    client: TestClient, instructor_id: str, headers: dict[str, str], filename: str = "c.pdf"
) -> dict[str, str]:
    resp = client.post(
        f"/api/v1/instructors/{instructor_id}/documents",
        headers=headers,
        files={
            "detran_credential": (filename, PDF, "application/pdf"),
            "criminal_record": ("../../etc/passwd.png", PNG, "image/png"),
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]


def test_upload_stores_the_file_contents(
    client: TestClient, db_session: Session, storage: InMemoryDocumentStorage
) -> None:
    instructor_id, headers = _instructor_headers(db_session)

    _upload(client, instructor_id, headers)

    document = db_session.exec(
        select(InstructorDocument).where(col(InstructorDocument.instructor_id) == instructor_id)
    ).one()
    assert document.detran_credential_url is not None
    assert document.criminal_record_url is not None
    assert storage.objects[document.detran_credential_url].content == PDF
    assert storage.objects[document.criminal_record_url].content == PNG


def test_object_keys_are_generated_not_taken_from_the_client(
    client: TestClient, db_session: Session, storage: InMemoryDocumentStorage
) -> None:
    instructor_id, headers = _instructor_headers(db_session)

    _upload(client, instructor_id, headers, filename="evil name;<script>.pdf")

    keys = list(storage.objects)
    assert len(keys) == 2
    for key in keys:
        assert key.startswith(f"instructors/{instructor_id}/")
        assert "evil" not in key
        assert "passwd" not in key
        assert ".." not in key
    assert {key.rsplit(".", 1)[1] for key in keys} == {"pdf", "png"}
    # The original filename is kept only as metadata
    assert {obj.original_filename for obj in storage.objects.values()} == {
        "evil name;<script>.pdf",
        "passwd.png",
    }


def test_upload_response_does_not_expose_storage_keys(
    client: TestClient, db_session: Session, storage: InMemoryDocumentStorage
) -> None:
    instructor_id, headers = _instructor_headers(db_session)

    data = _upload(client, instructor_id, headers)

    assert set(data) == {"instructor_id", "document_id", "uploaded_at"}
    assert not any(key in str(data) for key in storage.objects)


def test_admin_gets_short_lived_links_to_view_documents(
    client: TestClient, db_session: Session
) -> None:
    instructor_id, headers = _instructor_headers(db_session)
    _upload(client, instructor_id, headers)

    resp = client.get(
        f"/api/v1/admin/instructors/{instructor_id}/documents",
        headers=admin_headers(db_session),
    )

    assert resp.status_code == 200
    [document] = resp.json()["data"]
    assert document["detran_credential"]["url"].startswith("memory://")
    assert document["detran_credential"]["content_type"] == "application/pdf"
    assert document["criminal_record"]["content_type"] == "image/png"
    assert document["expires_in"] == 300
    assert document["review_status"] == "PENDENTE"


def test_only_admins_can_view_documents(client: TestClient, db_session: Session) -> None:
    instructor_id, headers = _instructor_headers(db_session)
    _upload(client, instructor_id, headers)

    resp = client.get(f"/api/v1/admin/instructors/{instructor_id}/documents", headers=headers)

    assert resp.status_code == 403


@pytest.mark.parametrize("decision", ["approve", "reject"])
def test_review_deletes_the_stored_objects(
    client: TestClient,
    db_session: Session,
    storage: InMemoryDocumentStorage,
    decision: str,
) -> None:
    instructor_id, headers = _instructor_headers(db_session)
    _upload(client, instructor_id, headers)
    assert len(storage.objects) == 2

    resp = client.patch(
        f"/api/v1/admin/instructors/{instructor_id}/{decision}",
        headers=admin_headers(db_session),
        json={"reason": "ok"} if decision == "reject" else None,
    )

    assert resp.status_code == 200
    assert storage.objects == {}


def test_local_storage_links_resolve_through_the_api(
    client: TestClient, db_session: Session, tmp_path: Path
) -> None:
    local = LocalDocumentStorage(
        tmp_path, signing_key="k", base_url="http://testserver/api/v1/documents/local"
    )
    client.app.dependency_overrides[get_document_storage] = lambda: local  # ty: ignore[unresolved-attribute]
    instructor_id, headers = _instructor_headers(db_session)
    _upload(client, instructor_id, headers)
    [document] = client.get(
        f"/api/v1/admin/instructors/{instructor_id}/documents",
        headers=admin_headers(db_session),
    ).json()["data"]

    url = document["detran_credential"]["url"].removeprefix("http://testserver")
    resp = client.get(url)

    assert resp.status_code == 200
    assert resp.content == PDF
    assert resp.headers["content-type"] == "application/pdf"
    assert client.get(url.replace("signature=", "signature=0")).status_code == 404
