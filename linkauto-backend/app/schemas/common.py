from __future__ import annotations

from typing import Any, Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    total: int | None = Field(default=None, ge=0)


class ErrorDetail(BaseModel):
    code: str
    message: str


class SuccessEnvelope(BaseModel, Generic[T]):
    data: T
    error: None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class ErrorEnvelope(BaseModel):
    data: None = None
    error: ErrorDetail
    meta: dict[str, Any] = Field(default_factory=dict)


def success_envelope(data: Any, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    envelope = SuccessEnvelope[Any](data=data, meta=meta or {})
    return envelope.model_dump(mode="json")


def error_envelope(code: str, message: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    envelope = ErrorEnvelope(error=ErrorDetail(code=code, message=message), meta=meta or {})
    return envelope.model_dump(mode="json")


def success_response(
    data: Any, meta: dict[str, Any] | None = None, status_code: int = 200
) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=jsonable_encoder(success_envelope(data, meta)))


def error_response(
    code: str, message: str, status_code: int, meta: dict[str, Any] | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content=jsonable_encoder(error_envelope(code, message, meta))
    )
