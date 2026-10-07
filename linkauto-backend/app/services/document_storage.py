"""Private object storage for instructor credential documents (S3, local disk or memory)."""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Protocol
from urllib.parse import quote, urlencode

import boto3
from botocore.config import Config

from app.models import generate_uuid7

if TYPE_CHECKING:
    from app.core import Settings

logger = logging.getLogger("app.services.document_storage")

# Generated keys only use these extensions, chosen from the validated MIME type
EXTENSION_BY_MIME = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
}

DEFAULT_LINK_TTL_SECONDS = 300


def build_object_key(instructor_id: str, kind: str, content_type: str) -> str:
    """Return a server-generated object key; nothing in it comes from the client filename."""
    extension = EXTENSION_BY_MIME[content_type]
    return f"instructors/{instructor_id}/{kind}-{generate_uuid7()}.{extension}"


class DocumentStorage(Protocol):
    """Private storage of uploaded documents, addressed by server-generated keys."""

    def put(
        self, key: str, content: bytes, *, content_type: str, original_filename: str | None
    ) -> None:
        """Store ``content`` under ``key``; the client filename is kept only as metadata."""
        ...

    def delete(self, keys: list[str]) -> None:
        """Delete the objects (missing keys are ignored)."""
        ...

    def presigned_url(self, key: str, *, expires_in: int = DEFAULT_LINK_TTL_SECONDS) -> str:
        """Return a short-lived URL to view the object."""
        ...


@dataclass
class StoredObject:
    """An object held by ``InMemoryDocumentStorage``."""

    content: bytes
    content_type: str
    original_filename: str | None


@dataclass
class InMemoryDocumentStorage:
    """Process-local storage for tests and development without S3."""

    objects: dict[str, StoredObject] = field(default_factory=dict)

    def put(
        self, key: str, content: bytes, *, content_type: str, original_filename: str | None
    ) -> None:
        """Keep the object in memory."""
        self.objects[key] = StoredObject(content, content_type, original_filename)

    def delete(self, keys: list[str]) -> None:
        """Drop the objects."""
        for key in keys:
            self.objects.pop(key, None)

    def presigned_url(self, key: str, *, expires_in: int = DEFAULT_LINK_TTL_SECONDS) -> str:
        """Return a fake, non-resolvable URL (``memory://``)."""
        return f"memory://{quote(key)}?expires_in={expires_in}"


class LocalDocumentStorage:
    """Store objects on the local disk; links are HMAC-signed and short-lived.

    Used whenever no S3 bucket is configured. In containers, mount a persistent volume at
    ``DOCUMENT_STORAGE_PATH`` and run a single replica (or share the volume).
    """

    def __init__(self, root: Path, *, signing_key: str, base_url: str) -> None:
        """Store files under ``root``; links point to ``base_url`` + key."""
        self._root = root.resolve()
        self._signing_key = signing_key.encode()
        self._base_url = base_url.rstrip("/")

    def _path(self, key: str) -> Path:
        path = (self._root / key).resolve()
        if not path.is_relative_to(self._root):
            msg = "Invalid object key."
            raise ValueError(msg)
        return path

    def put(
        self,
        key: str,
        content: bytes,
        *,
        content_type: str,  # noqa: ARG002 - implied by the generated extension
        original_filename: str | None,  # noqa: ARG002 - not kept on disk
    ) -> None:
        """Write the file, creating parent directories."""
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def delete(self, keys: list[str]) -> None:
        """Remove the files."""
        for key in keys:
            self._path(key).unlink(missing_ok=True)

    def sign(self, key: str, expires_at: int) -> str:
        """Return the HMAC signature authorizing access to ``key`` until ``expires_at``."""
        message = f"{key}:{expires_at}".encode()
        return hmac.new(self._signing_key, message, hashlib.sha256).hexdigest()

    def presigned_url(self, key: str, *, expires_in: int = DEFAULT_LINK_TTL_SECONDS) -> str:
        """Return a signed, expiring link to the local file download endpoint."""
        expires_at = int(time.time()) + expires_in
        query = urlencode({"expires": expires_at, "signature": self.sign(key, expires_at)})
        return f"{self._base_url}/{quote(key)}?{query}"

    def read(self, key: str, *, expires_at: int, signature: str) -> bytes:
        """Return the file if the signature is valid and not expired, else raise ``ValueError``."""
        if expires_at < time.time() or not hmac.compare_digest(
            self.sign(key, expires_at), signature
        ):
            msg = "Invalid or expired link."
            raise ValueError(msg)
        path = self._path(key)
        if not path.is_file():
            msg = "Document not found."
            raise ValueError(msg)
        return path.read_bytes()


class S3DocumentStorage:
    """Store objects in a private S3 bucket, server-side encrypted."""

    def __init__(self, settings: Settings) -> None:
        """Create the S3 client for ``S3_BUCKET``."""
        if not settings.s3_bucket:
            msg = "S3_BUCKET is not configured."
            raise ValueError(msg)
        self._bucket = settings.s3_bucket
        self._client = boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            # SigV4 presigned URLs on the regional endpoint (SigV2 is deprecated)
            config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
        )

    def put(
        self, key: str, content: bytes, *, content_type: str, original_filename: str | None
    ) -> None:
        """Upload the object; the original filename is stored as (ASCII-safe) metadata."""
        metadata = {"original-filename": quote(original_filename)} if original_filename else {}
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=content,
            ContentType=content_type,
            Metadata=metadata,
            ServerSideEncryption="AES256",
        )

    def delete(self, keys: list[str]) -> None:
        """Delete the objects in one batch request."""
        if not keys:
            return
        response = self._client.delete_objects(
            Bucket=self._bucket,
            Delete={"Objects": [{"Key": key} for key in keys], "Quiet": True},
        )
        for error in response.get("Errors", []):
            logger.warning(
                "Failed to delete document object",
                extra={"event": "documents.delete.failure", "code": error.get("Code")},
            )

    def presigned_url(self, key: str, *, expires_in: int = DEFAULT_LINK_TTL_SECONDS) -> str:
        """Return a presigned GET URL that expires after ``expires_in`` seconds."""
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in,
        )


def build_document_storage(settings: Settings) -> DocumentStorage:
    """Return the storage chosen by ``DOCUMENT_STORAGE``. S3 is optional.

    ``auto`` uses S3 when ``S3_BUCKET`` is set and the local disk otherwise; ``local`` keeps
    files under ``DOCUMENT_STORAGE_PATH``; ``memory`` keeps them in the process (tests).
    """
    backend = settings.document_storage
    if backend == "auto":
        backend = "s3" if settings.s3_bucket else "local"
    if backend == "s3":
        return S3DocumentStorage(settings)
    if backend == "memory":
        return InMemoryDocumentStorage()
    return LocalDocumentStorage(
        Path(settings.document_storage_path),
        signing_key=settings.jwt_secret,
        base_url=f"{settings.public_api_url.rstrip('/')}{settings.api_v1_prefix}/documents/local",
    )
