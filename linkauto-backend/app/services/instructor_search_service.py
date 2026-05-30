from __future__ import annotations

import math

from sqlalchemy.orm import Session

from app.models.user import DetranStatus, InstructorProfile

EARTH_RADIUS_KM = 6371.0


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km using Haversine formula."""
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class InstructorSearchService:
    def __init__(self, db: Session):
        self._db = db

    def search(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 20.0,
        min_rating: float | None = None,
        max_price: float | None = None,
    ) -> list[InstructorProfile]:
        query = self._db.query(InstructorProfile).filter(
            InstructorProfile.detran_status == DetranStatus.APROVADO.value,
            InstructorProfile.is_active.is_(True),
            InstructorProfile.latitude.isnot(None),
            InstructorProfile.longitude.isnot(None),
        )

        if min_rating is not None:
            query = query.filter(InstructorProfile.rating_avg >= min_rating)
        if max_price is not None:
            query = query.filter(InstructorProfile.price_per_hour <= max_price)

        candidates = query.all()

        # SQLite fallback: filter by Haversine in Python
        results = []
        for p in candidates:
            dist = _haversine_distance(latitude, longitude, float(p.latitude), float(p.longitude))
            if dist <= radius_km:
                results.append(p)

        return results
