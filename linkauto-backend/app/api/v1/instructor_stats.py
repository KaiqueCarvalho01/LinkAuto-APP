"""Instructor dashboard statistics endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Response

from app.api.deps.types import CurrentInstrutor, DbSession
from app.schemas.common import success_response
from app.services.instructor_stats_service import InstructorStatsService

router = APIRouter(prefix="/instructor", tags=["instructor-stats"])


@router.get("/stats")
def get_instructor_stats(
    user: CurrentInstrutor,
    db: DbSession,
) -> Response:
    """Return the calling instructor's lesson, hour, student and pending-booking counts.

    Requires the INSTRUTOR role.
    """
    service = InstructorStatsService(db)
    stats = service.get_stats(instructor_id=user.user_id)
    return success_response(stats.model_dump())
