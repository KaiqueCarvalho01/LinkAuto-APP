"""Application services package."""

from app.services.admin_validation_service import AdminValidationService
from app.services.auth_service import AuthService
from app.services.booking_lock_service import (
    BookingLockService,
    InMemorySlotReservationStore,
    SlotReservationConflictError,
    SqlAlchemySlotReservationStore,
)
from app.services.booking_message_service import BookingMessageAccessError, BookingMessageService
from app.services.booking_scheduler import BookingScheduler
from app.services.booking_service import (
    BookingAccessError,
    BookingService,
    PenalizedStudentError,
    SlotValidationError,
)
from app.services.document_cleanup_service import DocumentCleanupService
from app.services.identity_repository import (
    DuplicateEmailError,
    IdentityRepository,
    UserNotFoundError,
)
from app.services.instructor_document_service import (
    DocumentTooLargeError,
    DocumentValidationError,
    InstructorDocumentService,
)
from app.services.notification_service import (
    BackgroundEmailGateway,
    DisabledEmailGateway,
    InMemoryEmailGateway,
    NotificationDispatchResult,
    NotificationEvent,
    NotificationPayload,
    NotificationService,
    SESEmailGateway,
    build_email_gateway,
)
from app.services.penalty_service import PenaltyService
from app.services.profile_service import ProfileService
from app.services.review_service import (
    ReviewAccessError,
    ReviewDuplicateError,
    ReviewService,
    ReviewStateError,
)
from app.services.slot_service import SlotOverlapError, SlotService

__all__ = [
    "AdminValidationService",
    "AuthService",
    "BackgroundEmailGateway",
    "BookingAccessError",
    "BookingLockService",
    "BookingMessageAccessError",
    "BookingMessageService",
    "BookingScheduler",
    "BookingService",
    "DisabledEmailGateway",
    "DocumentCleanupService",
    "DocumentTooLargeError",
    "DocumentValidationError",
    "DuplicateEmailError",
    "IdentityRepository",
    "InMemoryEmailGateway",
    "InMemorySlotReservationStore",
    "InstructorDocumentService",
    "NotificationDispatchResult",
    "NotificationEvent",
    "NotificationPayload",
    "NotificationService",
    "PenalizedStudentError",
    "PenaltyService",
    "ProfileService",
    "ReviewAccessError",
    "ReviewDuplicateError",
    "ReviewService",
    "ReviewStateError",
    "SESEmailGateway",
    "SlotOverlapError",
    "SlotReservationConflictError",
    "SlotService",
    "SlotValidationError",
    "SqlAlchemySlotReservationStore",
    "UserNotFoundError",
    "build_email_gateway",
]
