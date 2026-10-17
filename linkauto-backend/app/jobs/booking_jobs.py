"""Admin-only endpoints that trigger the booking automation jobs on demand.

The jobs normally run on a schedule with ``python -m app.jobs run all``; these endpoints are
for manual runs. Both are safe to run at the same time.

Every job responds with the same run summary: ``processed`` and ``booking_ids`` for the
bookings handled successfully, ``failed`` and ``failed_booking_ids`` for those that failed.
"""

from typing import TYPE_CHECKING

from fastapi import APIRouter, Response

from app.api.deps.types import CurrentAdmin, DbSession
from app.jobs.runner import Job, run_job
from app.schemas.common import success_response
from app.services.dependencies import Notifications

if TYPE_CHECKING:
    from app.services.booking_scheduler import BookingSchedulerResult

router = APIRouter(tags=["Jobs"])


def _summary_response(result: BookingSchedulerResult) -> Response:
    """Return the run summary shared by all job endpoints."""
    return success_response(
        {
            "processed": result.processed,
            "booking_ids": result.booking_ids,
            "failed": result.failed,
            "failed_booking_ids": result.failed_booking_ids,
        },
        meta={},
    )


@router.post("/jobs/booking-timeout")
def run_booking_timeout(
    _: CurrentAdmin,
    db: DbSession,
    notifications: Notifications,
) -> Response:
    """Cancel PENDENTE bookings created more than 24 hours ago. Admin only.

    Their slots are released and both participants are notified.
    """
    result = run_job(Job.TIMEOUT, db, notifications)
    db.commit()
    return _summary_response(result)


@router.post("/jobs/booking-completion")
def run_booking_completion(
    _: CurrentAdmin,
    db: DbSession,
    notifications: Notifications,
) -> Response:
    """Mark CONFIRMADA bookings as REALIZADA once their last slot ended 2+ hours ago. Admin only."""
    result = run_job(Job.COMPLETION, db, notifications)
    db.commit()
    return _summary_response(result)


@router.post("/jobs/booking-reminder")
def run_booking_reminder(
    _: CurrentAdmin,
    db: DbSession,
    notifications: Notifications,
) -> Response:
    """E-mail a reminder for bookings whose lesson starts in about 24 hours. Admin only.

    Covers bookings starting 23 to 25 hours from now that have not been reminded yet.
    """
    result = run_job(Job.REMINDER, db, notifications)
    db.commit()
    return _summary_response(result)
