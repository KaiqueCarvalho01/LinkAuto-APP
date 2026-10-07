"""Query parameters for the instructor search endpoint."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class InstructorSearchFilters(BaseModel):
    """Filters and sorting for searching approved instructors near a location."""

    latitude: float = Field(description="Latitude do aluno")
    longitude: float = Field(description="Longitude do aluno")
    radius_km: float = Field(default=20.0, ge=1, le=100)
    min_rating: float | None = Field(default=None, ge=0, le=5)
    max_price: float | None = Field(default=None, ge=0)
    specialties: list[str] | None = Field(default=None, description="Filtro de especialidades")
    sort_by: str | None = Field(
        default="distance", pattern="^(rating|price_asc|price_desc|distance)$"
    )

    @field_validator("specialties")
    @classmethod
    def split_comma_separated(cls, value: list[str] | None) -> list[str] | None:
        """Accept both repeated and comma-separated values; drop blanks."""
        if value is None:
            return None
        cleaned = [part.strip() for item in value for part in item.split(",") if part.strip()]
        return cleaned or None
