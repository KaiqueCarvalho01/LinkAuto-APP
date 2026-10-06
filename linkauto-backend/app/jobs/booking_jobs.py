"""Admin-only endpoints that trigger the booking automation jobs on demand.

Every job responds with the same run summary: ``processed`` and ``booking_ids`` for the
bookings handled successfully, ``failed`` and ``failed_booking_ids`` for those that failed.
"""

from fastapi import APIRouter, Response

from app.api.deps.types import CurrentAdmin, DbSession
from app.schemas.common import success_response
from app.services.booking_automation_store import SqlAlchemyBookingAutomationPort
from app.services.booking_scheduler import BookingScheduler, BookingSchedulerResult
from app.services.dependencies import get_notification_service

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
) -> Response:
    """Cancel PENDENTE bookings created more than 24 hours ago. Admin only."""
    port = SqlAlchemyBookingAutomationPort(db)
    scheduler = BookingScheduler(port)
    result = scheduler.run_pending_timeout()
    db.commit()
    return _summary_response(result)


@router.post("/jobs/booking-completion")
def run_booking_completion(
    _: CurrentAdmin,
    db: DbSession,
) -> Response:
    """Mark CONFIRMADA bookings as REALIZADA once their last slot ended 2+ hours ago. Admin only."""
    port = SqlAlchemyBookingAutomationPort(db)
    scheduler = BookingScheduler(port)
    result = scheduler.run_confirmed_completion()
    db.commit()
    return _summary_response(result)


@router.post("/jobs/booking-reminder")
def run_booking_reminder(
    _: CurrentAdmin,
    db: DbSession,
) -> Response:
    """E-mail a reminder for bookings whose lesson starts in about 24 hours. Admin only.

    Covers bookings starting 23 to 25 hours from now that have not been reminded yet.
    """
    port = SqlAlchemyBookingAutomationPort(db)
    scheduler = BookingScheduler(port, notification_service=get_notification_service())
    result = scheduler.run_lesson_reminders()
    db.commit()
    return _summary_response(result)
