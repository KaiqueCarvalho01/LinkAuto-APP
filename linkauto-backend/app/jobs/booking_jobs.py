from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.authn import AuthenticatedUser, get_current_user
from app.api.deps.authz import require_roles
from app.core.database import get_db
from app.schemas.common import success_response
from app.services.booking_automation_store import SqlAlchemyBookingAutomationPort
from app.services.booking_scheduler import BookingScheduler

router = APIRouter(tags=["Jobs"])


@router.post("/jobs/booking-timeout")
def run_booking_timeout(
    current_user: AuthenticatedUser = Depends(get_current_user),
    _authz=Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
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
    current_user: AuthenticatedUser = Depends(get_current_user),
    _authz=Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    port = SqlAlchemyBookingAutomationPort(db)
    scheduler = BookingScheduler(port)
    result = scheduler.run_confirmed_completion()
    db.commit()
    return success_response(
        {"processed": result.processed, "errors": result.errors},
        meta={},
    )
