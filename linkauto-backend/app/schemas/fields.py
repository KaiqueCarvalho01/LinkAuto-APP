"""Constrained field types shared by request schemas (ranges and lengths match the columns)."""

from __future__ import annotations

from typing import Annotated
from urllib.parse import urlparse

from pydantic import AfterValidator, Field

Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]

FullName = Annotated[str, Field(max_length=255)]
Phone = Annotated[str, Field(max_length=30)]
Place = Annotated[str, Field(max_length=120)]
LongText = Annotated[str, Field(max_length=2000)]
ShortText = Annotated[str, Field(max_length=500)]

# Up to 99,999.99 (the column is NUMERIC(10, 2)); never negative
PricePerHour = Annotated[float, Field(ge=0, le=99_999.99)]
RadiusKm = Annotated[int, Field(ge=1, le=200)]
Specialty = Annotated[str, Field(min_length=1, max_length=60)]
Specialties = Annotated[list[Specialty], Field(max_length=20)]


def _https_url(value: str) -> str:
    """Accept only absolute https:// URLs (no javascript:, data: or plain http)."""
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        msg = "Must be an https:// URL"
        raise ValueError(msg)
    return value


AvatarUrl = Annotated[str, Field(max_length=500), AfterValidator(_https_url)]
