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
    BookingNotFoundError,
    BookingService,
    BookingSide,
    InstructorUnavailableError,
    PenalizedStudentError,
    SlotValidationError,
)
from app.services.dependencies import Notifications

router = APIRouter(tags=["Bookings"])


@router.post("/bookings", status_code=201)
def create_booking(
    body: BookingCreateRequest,
    current_user: CurrentAluno,
    db: DbSession,
    notifications: Notifications,
) -> Response:
    """Create a PENDENTE booking for the calling student and reserve its slots.

    Requires the ALUNO role. `instructor_id` may be the instructor's public slug.
    Per RN02 the booking needs at least 2 consecutive one-hour slots, all available
    and belonging to that instructor; otherwise 422 is returned (also when a user
    with both roles tries to book their own slots). Returns 404 `INSTRUCTOR_NOT_FOUND`
    when the instructor doesn't exist or isn't DETRAN-approved and active (RN01), and
    403 when the student is under an active cancellation penalty (RN04). The
    instructor is notified of the new booking.
    """
    service = BookingService(db, notification_service=notifications)
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
    except InstructorUnavailableError as e:
        raise HTTPException(
            status_code=404, detail={"code": "INSTRUCTOR_NOT_FOUND", "message": str(e)}
        ) from e


def _default_sides(roles: list[str]) -> list[BookingSide]:
    sides = []
    if "ALUNO" in roles:
        sides.append(BookingSide.STUDENT)
    if "INSTRUTOR" in roles:
        sides.append(BookingSide.INSTRUCTOR)
    return sides or [BookingSide.STUDENT]


@router.get("/bookings")
def list_bookings(
    current_user: CurrentUser,
    db: DbSession,
    status: Annotated[str | None, Query()] = None,
    as_: Annotated[BookingSide | None, Query(alias="as")] = None,
) -> Response:
    """List the caller's bookings, newest first, optionally filtered by status.

    Requires authentication. ``as=student`` returns the bookings the caller made,
    ``as=instructor`` the bookings made with them. Without ``as``, the sides follow
    the caller's roles: ALUNO, INSTRUTOR, or both for users with both roles. Compare
    ``student_id``/``instructor_id`` with your own ID to tell the sides apart.
    ``meta.as`` lists the sides returned.
    """
    service = BookingService(db)
    sides = [as_] if as_ else _default_sides(current_user.roles)
    bookings = service.list_bookings(current_user.user_id, sides, status_filter=status)
    return success_response(
        [BookingResource.model_validate(b).model_dump(mode="json") for b in bookings],
        meta={"total": len(bookings), "as": [side.value for side in sides]},
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
    notifications: Notifications,
) -> Response:
    """Confirm a PENDENTE booking and notify the student.

    Requires the INSTRUTOR role and must be called by the booking's instructor.
    Returns 404 when the booking does not exist, 403 when the caller is not the
    booking's instructor, and 422 when the booking cannot move to CONFIRMADA.
    """
    service = BookingService(db, notification_service=notifications)
    try:
        booking = service.confirm_booking(booking_id, current_user.user_id)
        db.commit()
        return success_response(
            BookingResource.model_validate(booking).model_dump(mode="json"),
            meta={},
        )
    except BookingNotFoundError as e:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(e)}) from e
    except BookingAccessError as e:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": str(e)}) from e
    except BookingTransitionError as e:
        raise HTTPException(
            status_code=422, detail={"code": "INVALID_TRANSITION", "message": str(e)}
        ) from e


@router.patch("/bookings/{booking_id}/cancel")
def cancel_booking(
    booking_id: str,
    body: BookingCancelRequest,
    current_user: CurrentUser,
    db: DbSession,
    notifications: Notifications,
) -> Response:
    """Cancel a PENDENTE or CONFIRMADA booking and release its slots.

    Requires authentication. The cancellation is attributed from the booking: to
    ALUNO when the caller is its student, to INSTRUTOR when they are its instructor
    (users with both roles cancel as the side they are on). Per RN04, a student who
    cancels less than 24 hours before the first slot receives a 7-day booking
    penalty. The other party is notified. Returns 404 when the booking does not
    exist, 403 when the caller is not a participant and 422 when it is already in a
    terminal status.
    """
    service = BookingService(db, notification_service=notifications)
    try:
        booking = service.cancel_booking(booking_id, current_user.user_id, body.reason)
        db.commit()
        return success_response(
            BookingResource.model_validate(booking).model_dump(mode="json"),
            meta={},
        )
    except BookingNotFoundError as e:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(e)}) from e
    except BookingAccessError as e:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": str(e)}) from e
    except BookingTransitionError as e:
        raise HTTPException(
            status_code=422, detail={"code": "INVALID_TRANSITION", "message": str(e)}
        ) from e
