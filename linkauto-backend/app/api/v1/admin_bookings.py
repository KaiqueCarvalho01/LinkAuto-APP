"""Admin endpoints for overriding booking status."""

from fastapi import APIRouter, HTTPException, Response

from app.api.deps.types import CurrentAdmin, DbSession
from app.core.security_logger import log_admin_action
from app.domain.booking import BookingTransitionError
from app.schemas.booking import BookingAdminOverrideRequest, BookingResource
from app.schemas.common import success_response
from app.services.admin_booking_service import AdminBookingService
from app.services.booking_service import BookingNotFoundError
from app.services.dependencies import get_notification_service

router = APIRouter(tags=["Admin Bookings"])


@router.patch("/admin/bookings/{booking_id}/override-status")
def admin_override_booking(
    booking_id: str,
    body: BookingAdminOverrideRequest,
    current_user: CurrentAdmin,
    db: DbSession,
) -> Response:
    """Force a booking into a terminal status (REALIZADA or CANCELADA).

    Requires the ADMIN role. The reason is required (min. 3 characters). The override
    is stored in an audit trail (admin, previous and new status, reason, time) and
    echoed in the response metadata. Unlike regular transitions, an admin may move a
    booking between the two terminal statuses. Overriding to CANCELADA records the
    cancellation as ADMIN, releases future reserved slots and notifies both parties.

    Returns 404 when the booking does not exist and 422 when the transition is not
    allowed or the body is invalid.
    """
    service = AdminBookingService(db, notification_service=get_notification_service())
    try:
        booking = service.override_status(
            booking_id, body.status, body.reason, admin_id=current_user.user_id
        )
        db.commit()
    except BookingNotFoundError as e:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(e)}) from e
    except BookingTransitionError as e:
        raise HTTPException(
            status_code=422, detail={"code": "INVALID_TRANSITION", "message": str(e)}
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=422, detail={"code": "VALIDATION_ERROR", "message": str(e)}
        ) from e
    log_admin_action(
        admin_id=current_user.user_id, action="override_booking_status", target_id=booking_id
    )
    return success_response(
        BookingResource.model_validate(booking).model_dump(mode="json"),
        meta={"overridden_by": current_user.user_id, "reason": body.reason},
    )
