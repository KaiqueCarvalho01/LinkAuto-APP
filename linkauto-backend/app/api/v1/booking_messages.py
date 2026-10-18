"""Endpoints for messages exchanged between booking participants."""

from typing import Annotated

from fastapi import APIRouter, Query, Response

from app.api.deps.types import CurrentUser, DbSession
from app.core.rate_limit import check_message_limit
from app.schemas.booking_message import BookingMessageCreateRequest, MessageResource
from app.schemas.common import error_response, success_response
from app.services.booking_message_service import (
    BookingMessageAccessError,
    BookingMessageClosedError,
    BookingMessageService,
)
from app.services.dependencies import Notifications

router = APIRouter(prefix="/bookings/{booking_id}", tags=["Booking Messages"])


@router.post("/messages", response_model=dict, status_code=201)
def send_booking_message(
    booking_id: str,
    payload: BookingMessageCreateRequest,
    current_user: CurrentUser,
    db: DbSession,
    notifications: Notifications,
) -> Response:
    """Post a message (up to 2000 characters) on a booking and notify the other participant.

    Any authenticated user may call it, but only the booking's student or instructor
    may post. Limited to 20 messages per minute per user (429). Returns 403 when the
    caller is not a participant, 404 when the booking does not exist and 409 when it
    was cancelled (its conversation is closed). The e-mail to the other participant
    includes at most the first 300 characters.
    """
    check_message_limit(current_user.user_id)
    service = BookingMessageService(db, notification_service=notifications)
    try:
        msg = service.send_message(
            booking_id=booking_id,
            sender_id=current_user.user_id,
            content=payload.content,
        )
        db.commit()
        return success_response(MessageResource.model_validate(msg), status_code=201)
    except BookingMessageAccessError as e:
        return error_response(code="FORBIDDEN", message=str(e), status_code=403)
    except BookingMessageClosedError as e:
        return error_response(code="CONFLICT", message=str(e), status_code=409)
    except ValueError as e:
        return error_response(code="NOT_FOUND", message=str(e), status_code=404)


@router.get("/messages", response_model=dict)
def list_booking_messages(
    booking_id: str,
    current_user: CurrentUser,
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Response:
    """List a booking's messages in chronological order, paginated.

    Only the booking's student or instructor may read them. Returns 403 when the
    caller is not a participant and 404 when the booking does not exist.
    """
    service = BookingMessageService(db)
    try:
        messages = service.list_messages(
            booking_id=booking_id,
            user_id=current_user.user_id,
            page=page,
            page_size=page_size,
        )
        resources = [MessageResource.model_validate(m) for m in messages]
        return success_response(resources)
    except BookingMessageAccessError as e:
        return error_response(code="FORBIDDEN", message=str(e), status_code=403)
    except ValueError as e:
        return error_response(code="NOT_FOUND", message=str(e), status_code=404)
