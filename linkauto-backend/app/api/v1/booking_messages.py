from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps.authn import AuthenticatedUser, get_current_user
from app.core.database import get_db
from app.models.booking import Booking
from app.models.user import User
from app.schemas.booking_message import BookingMessageCreateRequest, MessageResource
from app.schemas.common import error_response, success_response
from app.services.booking_message_service import BookingMessageService, BookingMessageAccessError
from app.services.dependencies import get_notification_service

router = APIRouter(prefix="/bookings/{id}", tags=["Booking Messages"])


@router.post("/messages", response_model=dict, status_code=201)
def send_booking_message(
    id: str,
    payload: BookingMessageCreateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Fetch booking to determine recipient
    booking = db.query(Booking).filter(Booking.id == id).first()
    if not booking:
        return error_response(code="NOT_FOUND", message="Booking not found", status_code=404)

    # Determine recipient and sender emails
    sender = db.query(User).filter(User.id == current_user.user_id).first()
    sender_email = sender.email if sender else None

    recipient_id = booking.instructor_id if current_user.user_id == booking.student_id else booking.student_id
    recipient = db.query(User).filter(User.id == recipient_id).first()
    recipient_email = recipient.email if recipient else None

    service = BookingMessageService(db, notification_service=get_notification_service())
    try:
        msg = service.send_message(
            booking_id=id,
            sender_id=current_user.user_id,
            content=payload.content,
            sender_email=sender_email,
            recipient_email=recipient_email,
        )
        db.commit()
        return success_response(MessageResource.model_validate(msg), status_code=201)
    except BookingMessageAccessError as e:
        return error_response(code="FORBIDDEN", message=str(e), status_code=403)
    except ValueError as e:
        return error_response(code="NOT_FOUND", message=str(e), status_code=404)


@router.get("/messages", response_model=dict)
def list_booking_messages(
    id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BookingMessageService(db)
    try:
        messages = service.list_messages(
            booking_id=id,
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
