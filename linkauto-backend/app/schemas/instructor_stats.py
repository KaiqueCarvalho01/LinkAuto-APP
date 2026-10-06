"""Schemas for the instructor dashboard statistics."""

from pydantic import BaseModel, ConfigDict


class InstructorStatsResponse(BaseModel):
    """Dashboard statistics for the authenticated instructor.

    Completed lessons and hours count REALIZADA bookings (hours = reserved 1-hour slots);
    unique students exclude CANCELADA bookings; pending counts PENDENTE bookings.
    """

    model_config = ConfigDict(extra="forbid")

    total_lessons: int
    total_hours: int
    unique_students: int
    pending_bookings: int
