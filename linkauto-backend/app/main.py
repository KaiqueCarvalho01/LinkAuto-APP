from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError

from app.api import api_router
from app.core import get_settings
from app.schemas.common import error_response


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
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
