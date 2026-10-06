from typing import Annotated

from fastapi import APIRouter, Query

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


@router.post("/bookings/{id}/reviews", response_model=dict, status_code=201)
def create_booking_review(
    id: str,
    payload: ReviewCreateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    # Fetch booking to determine recipient
    booking = db.query(Booking).filter(Booking.id == id).first()
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
            booking_id=id,
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


@router.get("/instructors/{id}/reviews", response_model=dict)
def list_instructor_reviews(
    id: str,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    service = ReviewService(db)
    reviews = service.list_instructor_reviews(
        instructor_id=id,
        page=page,
        page_size=page_size,
    )
    resources = [ReviewResource.model_validate(r) for r in reviews]
    return success_response(resources)
