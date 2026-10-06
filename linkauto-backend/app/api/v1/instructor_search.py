from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps.types import DbSession
from app.core.slug import generate_profile_slug
from app.schemas.common import success_response
from app.services.instructor_search_service import InstructorSearchService

router = APIRouter(tags=["Instructor Search"])


@router.get("/instructors/search")
def search_instructors(
    latitude: Annotated[float, Query(description="Latitude do aluno")],
    longitude: Annotated[float, Query(description="Longitude do aluno")],
    db: DbSession,
    radius_km: Annotated[float, Query(ge=1, le=100)] = 20.0,
    min_rating: Annotated[float | None, Query(ge=0, le=5)] = None,
    max_price: Annotated[float | None, Query(ge=0)] = None,
    specialties: Annotated[list[str] | None, Query(description="Filtro de especialidades")] = None,
    sort_by: Annotated[
        str | None, Query(pattern="^(rating|price_asc|price_desc|distance)$")
    ] = "distance",
):
    # Parse potential comma-separated specialties in query params
    cleaned_specialties: list[str] = []
    if specialties:
        for s in specialties:
            for part in s.split(","):
                if part.strip():
                    cleaned_specialties.append(part.strip())

    service = InstructorSearchService(db)
    results = service.search(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        min_rating=min_rating,
        max_price=max_price,
        specialties=cleaned_specialties or None,
        sort_by=sort_by,
    )

    def _resolve_slug(p) -> str:
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
