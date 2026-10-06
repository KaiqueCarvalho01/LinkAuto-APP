from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response

from app.api.deps.types import CurrentAluno, CurrentInstrutor, CurrentUser, DbSession
from app.domain.booking import BookingTransitionError
from app.schemas.booking import (
    BookingCancelRequest,
    BookingCreateRequest,
    BookingResource,
)
from app.schemas.common import success_response
from app.services.booking_service import (
    BookingLocation,
    BookingService,
    PenalizedStudentError,
    SlotValidationError,
)

router = APIRouter(tags=["Bookings"])


@router.post("/bookings", status_code=201)
def create_booking(
    body: BookingCreateRequest,
    current_user: CurrentAluno,
    db: DbSession,
) -> Response:
    service = BookingService(db)
    try:
        booking = service.create_booking(
            student_id=current_user.user_id,
            instructor_id=body.instructor_id,
            slot_ids=body.slot_ids,
            location=BookingLocation(
                description=body.location_description,
                latitude=body.latitude,
                longitude=body.longitude,
            ),
        )
        db.commit()
        return success_response(
            BookingResource.model_validate(booking).model_dump(mode="json"),
            meta={},
            status_code=201,
        )
    except SlotValidationError as e:
        raise HTTPException(
            status_code=422, detail={"code": "SLOT_VALIDATION", "message": str(e)}
        ) from e
    except PenalizedStudentError as e:
        raise HTTPException(
            status_code=403, detail={"code": "STUDENT_PENALIZED", "message": str(e)}
        ) from e


@router.get("/bookings")
def list_bookings(
    current_user: CurrentUser,
    db: DbSession,
    status: Annotated[str | None, Query()] = None,
) -> Response:
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
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    service = BookingService(db)
    booking = service.get_booking(booking_id)
    if not booking:
        raise HTTPException(
            status_code=404, detail={"code": "NOT_FOUND", "message": "Booking not found"}
        )
    is_participant = current_user.user_id in {booking.student_id, booking.instructor_id}
    if not is_participant and "ADMIN" not in current_user.roles:
        raise HTTPException(
            status_code=403, detail={"code": "FORBIDDEN", "message": "Access denied"}
        )
    return success_response(
        BookingResource.model_validate(booking).model_dump(mode="json"),
        meta={},
    )


@router.patch("/bookings/{booking_id}/confirm")
def confirm_booking(
    booking_id: str,
    current_user: CurrentInstrutor,
    db: DbSession,
) -> Response:
    service = BookingService(db)
    try:
        booking = service.confirm_booking(booking_id, current_user.user_id)
        db.commit()
        return success_response(
            BookingResource.model_validate(booking).model_dump(mode="json"),
            meta={},
        )
    except BookingTransitionError as e:
        raise HTTPException(
            status_code=422, detail={"code": "INVALID_TRANSITION", "message": str(e)}
        ) from e
    except ValueError as e:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": str(e)}) from e


@router.patch("/bookings/{booking_id}/cancel")
def cancel_booking(
    booking_id: str,
    body: BookingCancelRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    service = BookingService(db)
    cancelled_by = "INSTRUTOR" if "INSTRUTOR" in current_user.roles else "ALUNO"
    try:
        booking = service.cancel_booking(
            booking_id, current_user.user_id, cancelled_by, body.reason
        )
        db.commit()
        return success_response(
            BookingResource.model_validate(booking).model_dump(mode="json"),
            meta={},
        )
    except BookingTransitionError as e:
        raise HTTPException(
            status_code=422, detail={"code": "INVALID_TRANSITION", "message": str(e)}
        ) from e
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(e)}) from e
