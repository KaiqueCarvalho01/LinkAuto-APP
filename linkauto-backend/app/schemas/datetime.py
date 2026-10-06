from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from pydantic import BeforeValidator, PlainSerializer


def parse_datetime(v: object) -> datetime:
    if isinstance(v, datetime):
        if v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v.astimezone(UTC)
    if isinstance(v, str):
        if v.endswith("Z"):
            v = v[:-1] + "+00:00"
        dt = datetime.fromisoformat(v)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    msg = "Invalid datetime format"
    raise ValueError(msg)


def serialize_datetime(dt: datetime) -> str:
    dt = dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt.astimezone(UTC)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


UtcDateTime = Annotated[
    datetime,
    BeforeValidator(parse_datetime),
    PlainSerializer(serialize_datetime, return_type=str, when_used="json"),
]
