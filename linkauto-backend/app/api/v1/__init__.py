from fastapi import APIRouter

from app.api.v1 import admin_instructors, auth, foundation, instructor_documents, users

api_v1_router = APIRouter()
api_v1_router.include_router(foundation.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(admin_instructors.router)
api_v1_router.include_router(instructor_documents.router)

__all__ = ["api_v1_router"]
