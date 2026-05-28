from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps.authn import AuthenticatedUser, get_current_user
from app.api.deps.authz import require_roles
from app.core.database import get_db
from app.domain.booking import BookingTransitionError
from app.schemas.booking import BookingAdminOverrideRequest, BookingResource
from app.schemas.common import success_response
from app.services.admin_booking_service import AdminBookingService

router = APIRouter(tags=["Admin Bookings"])


@router.patch("/admin/bookings/{booking_id}/override-status")
def admin_override_booking(
    booking_id: str,
    body: BookingAdminOverrideRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    _authz=Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    service = AdminBookingService(db)
    try:
        booking = service.override_status(booking_id, body.status, body.reason)
        db.commit()
        return success_response(
            BookingResource.model_validate(booking).model_dump(mode="json"),
            meta={"overridden_by": current_user.user_id, "reason": body.reason},
        )
    except BookingTransitionError as e:
        raise HTTPException(status_code=422, detail={"code": "INVALID_TRANSITION", "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(e)})
