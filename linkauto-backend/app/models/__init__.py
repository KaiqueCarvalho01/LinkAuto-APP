"""SQLModel table models and enums for the LinkAuto domain."""

from app.models.base import AuditTimestampsMixin, AuditUUIDBase, Base, generate_uuid7
from app.models.booking import (
    Booking,
    BookingSlot,
    BookingStatusOverride,
    CancelledBy,
    StudentPenalty,
)
from app.models.booking_message import BookingMessage
from app.models.instructor_document import InstructorDocument, InstructorDocumentRepository
from app.models.review import Review
from app.models.slot import Slot, SlotStatus
from app.models.user import (
    DetranStatus,
    InstructorProfile,
    LicenseType,
    StudentProfile,
    User,
    UserRole,
)

__all__ = [
    "AuditTimestampsMixin",
    "AuditUUIDBase",
    "Base",
    "Booking",
    "BookingMessage",
    "BookingSlot",
    "BookingStatusOverride",
    "CancelledBy",
    "DetranStatus",
    "InstructorDocument",
    "InstructorDocumentRepository",
    "InstructorProfile",
    "LicenseType",
    "Review",
    "Slot",
    "SlotStatus",
    "StudentPenalty",
    "StudentProfile",
    "User",
    "UserRole",
    "generate_uuid7",
]
