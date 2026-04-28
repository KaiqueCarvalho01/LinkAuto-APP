from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core import get_settings
from app.core.dev_db import initialize_sqlite_dev_database
from app.schemas.common import error_response


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        initialize_sqlite_dev_database(settings)
        yield

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException):
        detail = exc.detail if isinstance(exc.detail, dict) else {}
        return error_response(
            code=detail.get("code", "HTTP_ERROR"),
            message=detail.get("message", str(exc.detail)),
            status_code=exc.status_code,
            meta=detail.get("meta"),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(_: Request, exc: RequestValidationError):
        return error_response(
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            status_code=422,
            meta={"issues": exc.errors()},
        )

    @app.get("/health", tags=["health"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
