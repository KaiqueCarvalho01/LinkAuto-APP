from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps.authn import AuthenticatedUser, get_current_user
from app.api.deps.authz import require_roles
from app.core.database import get_db
from app.domain.booking import BookingTransitionError
from app.schemas.booking import (
    BookingCancelRequest,
    BookingCreateRequest,
    BookingResource,
)
from app.schemas.common import success_response
from app.services.booking_service import (
    BookingService,
    PenalizedStudentError,
    SlotValidationError,
)

router = APIRouter(tags=["Bookings"])


@router.post("/bookings", status_code=201)
def create_booking(
    body: BookingCreateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    _authz=Depends(require_roles("ALUNO")),
    db: Session = Depends(get_db),
):
    service = BookingService(db)
    try:
        booking = service.create_booking(
            student_id=current_user.user_id,
            instructor_id=body.instructor_id,
            slot_ids=body.slot_ids,
            location_description=body.location_description,
            latitude=body.latitude,
            longitude=body.longitude,
        )
        db.commit()
        return success_response(
            BookingResource.model_validate(booking).model_dump(mode="json"),
            meta={},
            status_code=201,
        )
    except SlotValidationError as e:
        raise HTTPException(status_code=422, detail={"code": "SLOT_VALIDATION", "message": str(e)})
    except PenalizedStudentError as e:
        raise HTTPException(status_code=403, detail={"code": "STUDENT_PENALIZED", "message": str(e)})


@router.get("/bookings")
def list_bookings(
    status: str | None = Query(None),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BookingService(db)
    role = "INSTRUTOR" if "INSTRUTOR" in current_user.roles else "ALUNO"
    bookings = service.list_bookings(current_user.user_id, role, status_filter=status)
    return success_response(
        [BookingResource.model_validate(b).model_dump(mode="json") for b in bookings],
        meta={"total": len(bookings)},
    )


@router.get("/bookings/{booking_id}")
def get_booking(
    booking_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BookingService(db)
    booking = service.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Booking not found"})
    if booking.student_id != current_user.user_id and booking.instructor_id != current_user.user_id:
        if "ADMIN" not in current_user.roles:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Access denied"})
    return success_response(
        BookingResource.model_validate(booking).model_dump(mode="json"),
        meta={},
    )


@router.patch("/bookings/{booking_id}/confirm")
def confirm_booking(
    booking_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    _authz=Depends(require_roles("INSTRUTOR")),
    db: Session = Depends(get_db),
):
    service = BookingService(db)
    try:
        booking = service.confirm_booking(booking_id, current_user.user_id)
        db.commit()
        return success_response(
            BookingResource.model_validate(booking).model_dump(mode="json"),
            meta={},
        )
    except BookingTransitionError as e:
        raise HTTPException(status_code=422, detail={"code": "INVALID_TRANSITION", "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": str(e)})


@router.patch("/bookings/{booking_id}/cancel")
def cancel_booking(
    booking_id: str,
    body: BookingCancelRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BookingService(db)
    cancelled_by = "INSTRUTOR" if "INSTRUTOR" in current_user.roles else "ALUNO"
    try:
        booking = service.cancel_booking(booking_id, current_user.user_id, cancelled_by, body.reason)
        db.commit()
        return success_response(
            BookingResource.model_validate(booking).model_dump(mode="json"),
            meta={},
        )
    except BookingTransitionError as e:
        raise HTTPException(status_code=422, detail={"code": "INVALID_TRANSITION", "message": str(e)})
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(e)})
