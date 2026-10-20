"""Public instructor search endpoint."""

from typing import Annotated

from fastapi import APIRouter, Query, Response

from app.api.deps.types import DbSession
from app.schemas.common import success_response
from app.schemas.instructor_search import InstructorSearchFilters
from app.services.instructor_search_service import InstructorSearchService

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

    data = [
        {
            "id": p.slug,
            "slug": p.slug,
            "full_name": p.full_name,
            "city": p.city,
            "state": p.state,
            "specialties": p.specialties,
            "price_per_hour": float(p.price_per_hour) if p.price_per_hour is not None else None,
            "rating_avg": p.rating_avg,
            "rating_count": p.rating_count,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "action_radius_km": p.action_radius_km,
        }
        for p in results
    ]
    return success_response(data, meta={"total": len(data)})
