from fastapi import APIRouter, HTTPException

from app.api.deps.types import CurrentAdmin, DbSession
from app.domain.booking import BookingTransitionError
from app.schemas.booking import BookingAdminOverrideRequest, BookingResource
from app.schemas.common import success_response
from app.services.admin_booking_service import AdminBookingService

router = APIRouter(tags=["Admin Bookings"])


@router.patch("/admin/bookings/{booking_id}/override-status")
def admin_override_booking(
    booking_id: str,
    body: BookingAdminOverrideRequest,
    current_user: CurrentAdmin,
    db: DbSession,
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
        raise HTTPException(
            status_code=422, detail={"code": "INVALID_TRANSITION", "message": str(e)}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(e)})
