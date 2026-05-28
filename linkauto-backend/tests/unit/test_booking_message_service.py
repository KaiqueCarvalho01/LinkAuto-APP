import pytest

from app.models.booking import Booking
from app.models.booking_message import BookingMessage
from app.services.booking_message_service import BookingMessageService, BookingMessageAccessError
from app.services.notification_service import NotificationService, InMemoryEmailGateway


@pytest.fixture
def mock_notification_service():
    gateway = InMemoryEmailGateway()
    return NotificationService(email_gateway=gateway), gateway


def test_send_message_creates_record_and_dispatches_email(db_session, mock_notification_service):
    """send_message persists message and triggers a new_booking_message notification to the opposing party."""
    notification_svc, gateway = mock_notification_service
    
    # Setup booking
    booking = Booking(
        id="booking-123",
        student_id="student-456",
        instructor_id="instructor-789",
        status="CONFIRMADA",
    )
    db_session.add(booking)
    db_session.flush()

    service = BookingMessageService(db_session, notification_service=notification_svc)
    
    # Sender is the student. Recipient is the instructor.
    msg = service.send_message(
        booking_id="booking-123",
        sender_id="student-456",
        content="Olá, professor!",
        sender_email="aluno@test.com",
        recipient_email="instrutor@test.com"
    )

    assert msg.id is not None
    assert msg.booking_id == "booking-123"
    assert msg.sender_id == "student-456"
    assert msg.content == "Olá, professor!"

    # Verify email notification was dispatched
    assert len(gateway.sent_messages) == 1
    email = gateway.sent_messages[0]
    assert email["recipients"] == ["instrutor@test.com"]
    assert "professor" in email["body"]
    assert "student-456" in email["body"]


def test_send_message_rejects_unauthorized_sender(db_session):
    """send_message raises access error if sender is not part of the booking."""
    booking = Booking(
        id="booking-123",
        student_id="student-456",
        instructor_id="instructor-789",
        status="CONFIRMADA",
    )
    db_session.add(booking)
    db_session.flush()

    service = BookingMessageService(db_session)
    
    with pytest.raises(BookingMessageAccessError):
        service.send_message(
            booking_id="booking-123",
            sender_id="intruder-999",
            content="Hackeando",
            sender_email="hacker@test.com",
            recipient_email="instrutor@test.com"
        )


def test_list_messages_retrieves_chronologically(db_session):
    """list_messages returns all messages in chronological order and checks authorization."""
    booking = Booking(
        id="booking-123",
        student_id="student-456",
        instructor_id="instructor-789",
        status="CONFIRMADA",
    )
    db_session.add(booking)
    db_session.flush()

    service = BookingMessageService(db_session)
    
    # Send multiple messages
    msg1 = BookingMessage(
        booking_id="booking-123",
        sender_id="student-456",
        content="Mensagem 1",
    )
    msg2 = BookingMessage(
        booking_id="booking-123",
        sender_id="instructor-789",
        content="Mensagem 2",
    )
    db_session.add_all([msg1, msg2])
    db_session.flush()

    # Authorized user lists
    messages = service.list_messages(booking_id="booking-123", user_id="student-456")
    assert len(messages) == 2
    assert messages[0].content == "Mensagem 1"
    assert messages[1].content == "Mensagem 2"

    # Unauthorized user gets blocked
    with pytest.raises(BookingMessageAccessError):
        service.list_messages(booking_id="booking-123", user_id="intruder-999")
