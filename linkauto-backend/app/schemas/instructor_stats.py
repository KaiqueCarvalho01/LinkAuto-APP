from pydantic import BaseModel, ConfigDict


class InstructorStatsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_lessons: int
    total_hours: int
    unique_students: int
    pending_bookings: int
