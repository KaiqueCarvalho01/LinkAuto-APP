from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser, require_roles
from app.core.database import get_db
from app.schemas.common import success_response
from app.services.instructor_stats_service import InstructorStatsService

router = APIRouter(prefix="/instructor", tags=["instructor-stats"])


@router.get("/stats")
def get_instructor_stats(
    user: AuthenticatedUser = Depends(require_roles("INSTRUTOR")),
    db: Session = Depends(get_db),
) -> Response:
    service = InstructorStatsService(db)
    stats = service.get_stats(instructor_id=user.user_id)
    return success_response(stats.model_dump())
