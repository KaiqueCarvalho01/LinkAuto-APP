from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PublicReviewAuthor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    slug: str
    full_name: str
    avatar_url: str | None = None


class PublicReviewItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    reviewer: PublicReviewAuthor
    rating: int
    comment: str | None = None
    created_at: str


class PublicInstructorProfileResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    slug: str
    full_name: str
    avatar_url: str | None = None
    city: str | None = None
    state: str | None = None
    bio: str | None = None
    specialties: list[str] = []
    price_per_hour: float | None = None
    rating_avg: float = 5.0
    rating_count: int = 0
    detran_approved: bool = True
    reviews: list[PublicReviewItem] = []


class PublicStudentProfileResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    slug: str
    full_name: str
    avatar_url: str | None = None
    city: str | None = None
    state: str | None = None
    license_type: str | None = None
    rating_avg: float = 5.0
    rating_count: int = 0
    completed_lessons_count: int = 0
    reviews: list[PublicReviewItem] = []
