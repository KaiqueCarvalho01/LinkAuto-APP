"""Schemas for the admin dashboard statistics."""

from pydantic import BaseModel, ConfigDict


class AdminStatsResponse(BaseModel):
    """Platform-wide counts of instructors by DETRAN validation status, students and bookings."""

    model_config = ConfigDict(extra="forbid")

    total_instructors: int
    pending_instructors: int
    approved_instructors: int
    rejected_instructors: int
    total_students: int
    total_bookings: int
