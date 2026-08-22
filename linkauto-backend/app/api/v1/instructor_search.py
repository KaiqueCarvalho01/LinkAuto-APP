from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import success_response
from app.services.instructor_search_service import InstructorSearchService

router = APIRouter(tags=["Instructor Search"])


@router.get("/instructors/search")
def search_instructors(
    latitude: float = Query(..., description="Latitude do aluno"),
    longitude: float = Query(..., description="Longitude do aluno"),
    radius_km: float = Query(20.0, ge=1, le=100),
    min_rating: float | None = Query(None, ge=0, le=5),
    max_price: float | None = Query(None, ge=0),
    specialties: list[str] | None = Query(None, description="Filtro de especialidades"),
    sort_by: str | None = Query("distance", pattern="^(rating|price_asc|price_desc|distance)$"),
    db: Session = Depends(get_db),
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
        specialties=cleaned_specialties if cleaned_specialties else None,
        sort_by=sort_by,
    )
    data = [
        {
            "user_id": p.user_id,
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
