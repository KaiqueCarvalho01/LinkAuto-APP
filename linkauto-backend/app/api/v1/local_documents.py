"""Download endpoint for documents kept on the local disk (when no S3 bucket is configured)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.services.dependencies import get_document_storage
from app.services.document_storage import DocumentStorage, LocalDocumentStorage

router = APIRouter(tags=["documents"])

_MIME_BY_EXTENSION = {"pdf": "application/pdf", "jpg": "image/jpeg", "png": "image/png"}


@router.get("/documents/local/{key:path}", include_in_schema=False)
def download_local_document(
    key: str,
    storage: Annotated[DocumentStorage, Depends(get_document_storage)],
    expires: Annotated[int, Query()],
    signature: Annotated[str, Query()],
) -> Response:
    """Serve a locally stored document for a valid, unexpired signed link.

    Only active with local storage (S3 serves its own presigned URLs). Returns 404 for
    any invalid, expired or unknown link.
    """
    not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"code": "NOT_FOUND", "message": "Document not found."},
    )
    if not isinstance(storage, LocalDocumentStorage):
        raise not_found
    try:
        content = storage.read(key, expires_at=expires, signature=signature)
    except ValueError as exc:
        raise not_found from exc
    media_type = _MIME_BY_EXTENSION.get(key.rsplit(".", 1)[-1], "application/octet-stream")
    return Response(
        content,
        media_type=media_type,
        headers={"Cache-Control": "no-store", "Content-Disposition": "inline"},
    )
