"""Geographic search of approved instructors with rating, price and specialty filters."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from app.models.user import DetranStatus, InstructorProfile

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.schemas.instructor_search import InstructorSearchFilters

EARTH_RADIUS_KM = 6371.0


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km using Haversine formula."""
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class InstructorSearchService:
    """Find publicly visible instructors near a location."""

    def __init__(self, db: Session) -> None:
        """Store the DB session used to query instructor profiles."""
        self._db = db

    def search(self, filters: InstructorSearchFilters) -> list[InstructorProfile]:
        """Return active, DETRAN-approved instructors within ``radius_km`` of the given point.

        Rating and price are filtered in SQL; distance (Haversine) and specialties
        (case-insensitive substring match on any requested specialty) are filtered in
        Python. Results are sorted by distance unless ``sort_by`` is ``rating``,
        ``price_asc`` or ``price_desc``.
        """
        latitude, longitude = filters.latitude, filters.longitude
        radius_km, min_rating, max_price = filters.radius_km, filters.min_rating, filters.max_price
        specialties, sort_by = filters.specialties, filters.sort_by
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

        # Clean specialties filter list
        target_specialties = [s.strip().lower() for s in (specialties or []) if s.strip()]

        # SQLite fallback: filter by Haversine and specialties in Python
        matched_entries: list[tuple[InstructorProfile, float]] = []
        for p in candidates:
            # Check specialty match if filter was provided
            if target_specialties:
                prof_specs = [s.lower() for s in (p.specialties or [])]
                # Match if any of the target specialties is present in profile specialties
                if not any(
                    ts in prof_specs or any(ts in ps for ps in prof_specs)
                    for ts in target_specialties
                ):
                    continue

            dist = _haversine_distance(latitude, longitude, float(p.latitude), float(p.longitude))
            if dist <= radius_km:
                matched_entries.append((p, dist))

        # Sort results
        if sort_by == "rating":
            matched_entries.sort(key=lambda item: item[0].rating_avg or 0.0, reverse=True)
        elif sort_by == "price_asc":
            matched_entries.sort(key=lambda item: float(item[0].price_per_hour or 0.0))
        elif sort_by == "price_desc":
            matched_entries.sort(
                key=lambda item: float(item[0].price_per_hour or 0.0), reverse=True
            )
        else:  # default or "distance"
            matched_entries.sort(key=lambda item: item[1])

        return [item[0] for item in matched_entries]
