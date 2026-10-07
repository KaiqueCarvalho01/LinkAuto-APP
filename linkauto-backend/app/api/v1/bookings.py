"""Booking endpoints for students and instructors."""

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
    BookingAccessError,
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
    """Create a PENDENTE booking for the calling student and reserve its slots.

    Requires the ALUNO role. `instructor_id` may be the instructor's public slug.
    Per RN02 the booking needs at least 2 consecutive one-hour slots, all available
    and belonging to that instructor; otherwise 422 is returned. Returns 403 when the
    student is under an active cancellation penalty (RN04). The instructor is
    notified of the new booking.
    """
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
    """List the caller's bookings, newest first, optionally filtered by status.

    Requires authentication. Users with the INSTRUTOR role see bookings where they
    are the instructor; everyone else sees bookings where they are the student.
    """
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
    """Return a single booking with its slots.

    Only the booking's student, its instructor or an ADMIN may view it. Returns 404
    when the booking does not exist and 403 for any other caller.
    """
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
    """Confirm a PENDENTE booking and notify the student.

    Requires the INSTRUTOR role and must be called by the booking's instructor.
    Returns 403 when the caller is not the booking's instructor or the booking does
    not exist, and 422 when the booking cannot move to CONFIRMADA.
    """
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
    """Cancel a PENDENTE or CONFIRMADA booking and release its slots.

    Requires authentication. The cancellation is attributed to INSTRUTOR when the
    caller has that role, otherwise to ALUNO. Per RN04, a student who cancels less
    than 24 hours before the first slot receives a 7-day booking penalty. The other
    party is notified. Returns 404 when the booking does not exist and 422 when it is
    already in a terminal status.
    """
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
    except BookingAccessError as e:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": str(e)}) from e
    except BookingTransitionError as e:
        raise HTTPException(
            status_code=422, detail={"code": "INVALID_TRANSITION", "message": str(e)}
        ) from e
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(e)}) from e
