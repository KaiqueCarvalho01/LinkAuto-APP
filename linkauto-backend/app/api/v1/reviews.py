"""Endpoints for booking reviews."""

from typing import Annotated

from fastapi import APIRouter, Query, Response

from app.api.deps.types import CurrentUser, DbSession
from app.schemas.common import error_response, success_response
from app.schemas.review import ReviewCreateRequest, ReviewResource
from app.services.dependencies import Notifications
from app.services.public_profile_service import PublicProfileService
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
    notifications: Notifications,
) -> Response:
    """Submit a review of the other participant of a completed booking.

    Any authenticated user may call it, but only the booking's student or instructor
    may review, once per booking. Reviewing the instructor updates their rating
    average, and the reviewed user is notified by email. Returns 404 when the booking
    does not exist, 409 when it is not REALIZADA or was already reviewed by the
    caller, and 403 when the caller is not a participant.
    """
    service = ReviewService(db, notification_service=notifications)
    try:
        review = service.create_review(
            booking_id=booking_id,
            reviewer_id=current_user.user_id,
            rating=payload.rating,
            comment=payload.comment,
        )
        db.commit()
        return success_response(ReviewResource.model_validate(review), status_code=201)
    except (ReviewStateError, ReviewDuplicateError) as e:
        return error_response(code="CONFLICT", message=str(e), status_code=409)
    except ReviewAccessError as e:
        return error_response(code="FORBIDDEN", message=str(e), status_code=403)
    except ValueError as e:
        return error_response(code="NOT_FOUND", message=str(e), status_code=404)


@router.get("/instructors/{slug}/reviews", response_model=dict)
def list_instructor_reviews(
    slug: str,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Response:
    """List the reviews an instructor received, newest first, paginated.

    Public. The instructor is identified by public slug only (internal IDs are not
    accepted), and must be DETRAN-approved and active (404 otherwise). Reviews use the
    same public shape as the profile page: reviewers by name and slug, no internal IDs.
    """
    try:
        reviews = PublicProfileService(db).list_instructor_reviews(
            slug, page=page, page_size=page_size
        )
    except ValueError as e:
        return error_response(code="NOT_FOUND", message=str(e), status_code=404)
    return success_response([review.model_dump() for review in reviews])
