from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser, require_roles
from app.core.database import get_db
from app.schemas.common import success_response
from app.services.admin_stats_service import AdminStatsService

router = APIRouter(prefix="/admin", tags=["admin-stats"])


@router.get("/stats")
def get_admin_stats(
    _: AuthenticatedUser = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
) -> Response:
    service = AdminStatsService(db)
    stats = service.get_stats()
    return success_response(stats.model_dump())
