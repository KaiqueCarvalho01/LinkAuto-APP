"""Standard API response envelopes and helpers to build them."""

from __future__ import annotations

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class PaginationMeta(BaseModel):
    """Pagination metadata: 1-based page, page size (1-100) and optional total count."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    total: int | None = Field(default=None, ge=0)


class ErrorDetail(BaseModel):
    """Machine-readable error code and human-readable message."""

    code: str
    message: str


class SuccessEnvelope[T](BaseModel):
    """Successful response envelope: payload in ``data``, ``error`` always null, plus ``meta``."""

    data: T
    error: None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class ErrorEnvelope(BaseModel):
    """Error response envelope: ``data`` always null, details in ``error``, plus ``meta``."""

    data: None = None
    error: ErrorDetail
    meta: dict[str, Any] = Field(default_factory=dict)


def success_envelope(data: object, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a JSON-serializable success envelope for the data."""
    envelope = SuccessEnvelope[Any](data=data, meta=meta or {})
    return envelope.model_dump(mode="json")


def error_envelope(code: str, message: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a JSON-serializable error envelope for the code and message."""
    envelope = ErrorEnvelope(error=ErrorDetail(code=code, message=message), meta=meta or {})
    return envelope.model_dump(mode="json")


def success_response(
    data: object, meta: dict[str, Any] | None = None, status_code: int = 200
) -> JSONResponse:
    """Return a JSONResponse wrapping the data in a success envelope."""
    return JSONResponse(
        status_code=status_code, content=jsonable_encoder(success_envelope(data, meta))
    )


def error_response(
    code: str, message: str, status_code: int, meta: dict[str, Any] | None = None
) -> JSONResponse:
    """Return a JSONResponse wrapping the code and message in an error envelope."""
    return JSONResponse(
        status_code=status_code, content=jsonable_encoder(error_envelope(code, message, meta))
    )
