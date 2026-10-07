"""Public instructor search endpoint."""

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Query, Response

from app.api.deps.types import DbSession
from app.core.slug import generate_profile_slug
from app.schemas.common import success_response
from app.schemas.instructor_search import InstructorSearchFilters
from app.services.instructor_search_service import InstructorSearchService

if TYPE_CHECKING:
    from app.models.user import InstructorProfile

router = APIRouter(tags=["Instructor Search"])


@router.get("/instructors/search")
def search_instructors(
    filters: Annotated[InstructorSearchFilters, Query()],
    db: DbSession,
) -> Response:
    """Search approved, active instructors within a radius of a location.

    Public. Supports filtering by minimum rating, maximum hourly price and
    specialties, and sorting by distance (default), rating or price. Instructors are
    identified by their public slug, never by internal ID.
    """
    results = InstructorSearchService(db).search(filters)

    def _resolve_slug(p: InstructorProfile) -> str:
        if not p.slug:
            p.slug = generate_profile_slug(p.full_name, p.city, default_prefix="instrutor")
            db.flush()
        return p.slug

    data = [
        {
            "id": _resolve_slug(p),
            "slug": _resolve_slug(p),
            "full_name": p.full_name,
            "city": p.city,
            "state": p.state,
            "specialties": p.specialties,
            "price_per_hour": float(p.price_per_hour) if p.price_per_hour else None,
            "rating_avg": p.rating_avg,
            "rating_count": p.rating_count,
            "latitude": float(p.latitude),
            "longitude": float(p.longitude),
            "action_radius_km": p.action_radius_km,
        }
        for p in results
    ]
    return success_response(data, meta={"total": len(data)})
