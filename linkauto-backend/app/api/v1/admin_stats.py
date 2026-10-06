from __future__ import annotations

from fastapi import APIRouter, Response

from app.api.deps.types import CurrentAdmin, DbSession
from app.schemas.common import success_response
from app.services.admin_stats_service import AdminStatsService

router = APIRouter(prefix="/admin", tags=["admin-stats"])


@router.get("/stats")
def get_admin_stats(
    _: CurrentAdmin,
    db: DbSession,
) -> Response:
    service = AdminStatsService(db)
    stats = service.get_stats()
    return success_response(stats.model_dump())
