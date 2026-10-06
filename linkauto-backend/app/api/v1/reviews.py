"""Endpoints for booking reviews."""

from typing import Annotated

from fastapi import APIRouter, Query, Response

from app.api.deps.types import CurrentUser, DbSession
from app.models.booking import Booking
from app.models.user import User
from app.schemas.common import error_response, success_response
from app.schemas.review import ReviewCreateRequest, ReviewResource
from app.services.dependencies import get_notification_service
from app.services.review_service import (
    ReviewAccessError,
    ReviewDuplicateError,
    ReviewService,
    ReviewStateError,
)

router = APIRouter(tags=["Reviews"])


@router.post("/bookings/{booking_id}/reviews", response_model=dict, status_code=201)
def create_booking_review(
    booking_id: str,
    payload: ReviewCreateRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> Response:
    """Submit a review of the other participant of a completed booking.

    Any authenticated user may call it, but only the booking's student or instructor
    may review, once per booking. Reviewing the instructor updates their rating
    average, and the reviewed user is notified by email. Returns 404 when the booking
    does not exist, 409 when it is not REALIZADA or was already reviewed by the
    caller, and 403 when the caller is not a participant.
    """
    # Fetch booking to determine recipient
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        return error_response(code="NOT_FOUND", message="Booking not found", status_code=404)

    # Determine recipient email
    recipient_id = (
        booking.instructor_id if current_user.user_id == booking.student_id else booking.student_id
    )
    recipient = db.query(User).filter(User.id == recipient_id).first()
    recipient_email = recipient.email if recipient else None

    service = ReviewService(db, notification_service=get_notification_service())
    try:
        review = service.create_review(
            booking_id=booking_id,
            reviewer_id=current_user.user_id,
            rating=payload.rating,
            comment=payload.comment,
            recipient_email=recipient_email,
        )
        db.commit()
        return success_response(ReviewResource.model_validate(review), status_code=201)
    except (ReviewStateError, ReviewDuplicateError) as e:
        return error_response(code="CONFLICT", message=str(e), status_code=409)
    except ReviewAccessError as e:
        return error_response(code="FORBIDDEN", message=str(e), status_code=403)
    except ValueError as e:
        return error_response(code="NOT_FOUND", message=str(e), status_code=404)


@router.get("/instructors/{instructor_id}/reviews", response_model=dict)
def list_instructor_reviews(
    instructor_id: str,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Response:
    """List reviews received by an instructor, newest first, paginated.

    Public.
    """
    service = ReviewService(db)
    reviews = service.list_instructor_reviews(
        instructor_id=instructor_id,
        page=page,
        page_size=page_size,
    )
    resources = [ReviewResource.model_validate(r) for r in reviews]
    return success_response(resources)
