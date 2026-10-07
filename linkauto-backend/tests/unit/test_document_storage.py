import time
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlsplit

import pytest
from botocore.stub import Stubber

from app.core.config import Settings
from app.services.document_storage import (
    InMemoryDocumentStorage,
    LocalDocumentStorage,
    S3DocumentStorage,
    build_document_storage,
    build_object_key,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_object_keys_are_unique_and_typed_by_mime() -> None:
    first = build_object_key("inst-1", "detran-credential", "application/pdf")
    second = build_object_key("inst-1", "detran-credential", "application/pdf")

    assert first != second
    assert first.startswith("instructors/inst-1/detran-credential-")
    assert first.endswith(".pdf")
    assert build_object_key("i", "k", "image/jpeg").endswith(".jpg")


def test_storage_is_chosen_from_settings(tmp_path: Path) -> None:
    assert isinstance(
        build_document_storage(Settings(DOCUMENT_STORAGE_PATH=str(tmp_path))),
        LocalDocumentStorage,
    )
    assert isinstance(
        build_document_storage(Settings(DOCUMENT_STORAGE="memory")), InMemoryDocumentStorage
    )
    assert isinstance(
        build_document_storage(Settings(S3_BUCKET="bucket", AWS_REGION="sa-east-1")),
        S3DocumentStorage,
    )


class TestLocalDocumentStorage:
    @pytest.fixture
    def storage(self, tmp_path: Path) -> LocalDocumentStorage:
        return LocalDocumentStorage(
            tmp_path, signing_key="secret", base_url="http://api/api/v1/documents/local"
        )

    def test_round_trip_with_a_signed_link(self, storage: LocalDocumentStorage) -> None:
        storage.put(
            "instructors/i/a.pdf",
            b"%PDF",
            content_type="application/pdf",
            original_filename="x.pdf",
        )

        query = parse_qs(urlsplit(storage.presigned_url("instructors/i/a.pdf")).query)
        content = storage.read(
            "instructors/i/a.pdf",
            expires_at=int(query["expires"][0]),
            signature=query["signature"][0],
        )

        assert content == b"%PDF"

    def test_rejects_tampered_or_expired_links(self, storage: LocalDocumentStorage) -> None:
        storage.put("k.pdf", b"x", content_type="application/pdf", original_filename=None)
        expires = int(time.time()) + 60

        with pytest.raises(ValueError, match="Invalid or expired"):
            storage.read("k.pdf", expires_at=expires, signature="0" * 64)
        past = int(time.time()) - 1
        with pytest.raises(ValueError, match="Invalid or expired"):
            storage.read("k.pdf", expires_at=past, signature=storage.sign("k.pdf", past))

    def test_rejects_keys_outside_the_root(self, storage: LocalDocumentStorage) -> None:
        with pytest.raises(ValueError, match="Invalid object key"):
            storage.put(
                "../escape.pdf", b"x", content_type="application/pdf", original_filename=None
            )

    def test_delete_removes_files(self, storage: LocalDocumentStorage, tmp_path: Path) -> None:
        storage.put("a/b.pdf", b"x", content_type="application/pdf", original_filename=None)
        storage.delete(["a/b.pdf", "missing.pdf"])

        assert not (tmp_path / "a" / "b.pdf").exists()


class TestS3DocumentStorage:
    @pytest.fixture
    def storage(self) -> S3DocumentStorage:
        return S3DocumentStorage(
            Settings(
                S3_BUCKET="linkauto-docs",
                AWS_REGION="sa-east-1",
                AWS_ACCESS_KEY_ID="test",
                AWS_SECRET_ACCESS_KEY="test",
            )
        )

    def test_put_uploads_privately_with_filename_metadata(self, storage: S3DocumentStorage) -> None:
        with Stubber(storage._client) as stub:  # noqa: SLF001
            stub.add_response(
                "put_object",
                {},
                {
                    "Bucket": "linkauto-docs",
                    "Key": "instructors/i/a.pdf",
                    "Body": b"%PDF",
                    "ContentType": "application/pdf",
                    "Metadata": {"original-filename": "Certid%C3%A3o.pdf"},
                    "ServerSideEncryption": "AES256",
                },
            )
            storage.put(
                "instructors/i/a.pdf",
                b"%PDF",
                content_type="application/pdf",
                original_filename="Certidão.pdf",
            )
            stub.assert_no_pending_responses()

    def test_delete_batches_keys(self, storage: S3DocumentStorage) -> None:
        with Stubber(storage._client) as stub:  # noqa: SLF001
            stub.add_response(
                "delete_objects",
                {},
                {
                    "Bucket": "linkauto-docs",
                    "Delete": {"Objects": [{"Key": "a"}, {"Key": "b"}], "Quiet": True},
                },
            )
            storage.delete(["a", "b"])
            stub.assert_no_pending_responses()

    def test_presigned_url_expires(self, storage: S3DocumentStorage) -> None:
        url = storage.presigned_url("instructors/i/a.pdf", expires_in=300)

        parts = urlsplit(url)
        assert parts.netloc == "linkauto-docs.s3.sa-east-1.amazonaws.com"
        query = parse_qs(parts.query)
        assert query["X-Amz-Algorithm"] == ["AWS4-HMAC-SHA256"]
        assert query["X-Amz-Expires"] == ["300"]
