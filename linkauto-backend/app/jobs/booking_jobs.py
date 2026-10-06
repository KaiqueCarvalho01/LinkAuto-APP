from fastapi import APIRouter, Response

from app.api.deps.types import CurrentAdmin, DbSession
from app.schemas.common import success_response
from app.services.booking_automation_store import SqlAlchemyBookingAutomationPort
from app.services.booking_scheduler import BookingScheduler
from app.services.dependencies import get_notification_service

router = APIRouter(tags=["Jobs"])


@router.post("/jobs/booking-timeout")
def run_booking_timeout(
    _: CurrentAdmin,
    db: DbSession,
) -> Response:
    port = SqlAlchemyBookingAutomationPort(db)
    scheduler = BookingScheduler(port)
    result = scheduler.run_pending_timeout()
    db.commit()
    return success_response(
        {"processed": result.processed, "errors": result.errors},
        meta={},
    )


@router.post("/jobs/booking-completion")
def run_booking_completion(
    _: CurrentAdmin,
    db: DbSession,
) -> Response:
    port = SqlAlchemyBookingAutomationPort(db)
    scheduler = BookingScheduler(port)
    result = scheduler.run_confirmed_completion()
    db.commit()
    return success_response(
        {"processed": result.processed, "errors": result.booking_ids},
        meta={},
    )


@router.post("/jobs/booking-reminder")
def run_booking_reminder(
    _: CurrentAdmin,
    db: DbSession,
) -> Response:
    port = SqlAlchemyBookingAutomationPort(db)

    scheduler = BookingScheduler(port, notification_service=get_notification_service())
    result = scheduler.run_lesson_reminders()
    db.commit()
    return success_response(
        {"processed": result.processed, "booking_ids": result.booking_ids},
        meta={},
    )
