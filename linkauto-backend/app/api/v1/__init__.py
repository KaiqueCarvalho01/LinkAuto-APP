from fastapi import APIRouter

from app.api.v1 import (
    admin_bookings,
    admin_instructors,
    admin_stats,
    auth,
    booking_messages,
    foundation,
    instructor_documents,
    instructor_search,
    reviews,
    slots,
    bookings,
    users,
)
from app.jobs import booking_jobs

api_v1_router = APIRouter()
api_v1_router.include_router(foundation.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(admin_instructors.router)
api_v1_router.include_router(admin_stats.router)
api_v1_router.include_router(instructor_documents.router)
api_v1_router.include_router(slots.router)
api_v1_router.include_router(bookings.router)
api_v1_router.include_router(admin_bookings.router)
api_v1_router.include_router(instructor_search.router)
api_v1_router.include_router(booking_messages.router)
api_v1_router.include_router(reviews.router)
api_v1_router.include_router(booking_jobs.router)

__all__ = ["api_v1_router"]
