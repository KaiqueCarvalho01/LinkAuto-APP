"""FastAPI application factory and ASGI entry point for the LinkAuto API."""

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.exc import IntegrityError
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.api import api_router
from app.core import Settings, get_settings
from app.core.dev_db import initialize_sqlite_dev_database
from app.core.logging import CorrelationIDMiddleware, setup_logging
from app.core.middleware import SecurityHeadersMiddleware
from app.core.rate_limit import limiter, trusted_proxy_middleware_hosts
from app.schemas.common import error_response

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI app with middleware, API routes, error handlers and a health check.

    On startup the lifespan hook initializes the SQLite development database. Errors are
    returned in the standard error envelope (429, HTTP errors, 422 validation, 409 conflict).
    With ``TRUSTED_PROXIES`` set, ``X-Forwarded-For`` from those proxies sets the client IP.
    """
    setup_logging()
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        initialize_sqlite_dev_database(settings)
        yield

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.limiter = limiter
    app.add_middleware(CorrelationIDMiddleware)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    trusted_proxies = trusted_proxy_middleware_hosts(settings)
    if trusted_proxies:
        # Added last, so it runs first: every other layer sees the real client IP.
        # Uvicorn should run without --proxy-headers so only this explicit list is trusted.
        app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=trusted_proxies)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(
        _request: Request, _exc: RateLimitExceeded
    ) -> JSONResponse:
        return error_response(
            code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Please try again later.",
            status_code=429,
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, dict) else {}
        return error_response(
            code=detail.get("code", "HTTP_ERROR"),
            message=detail.get("message", str(exc.detail)),
            status_code=exc.status_code,
            meta=detail.get("meta"),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(_: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            status_code=422,
            meta={"issues": exc.errors()},
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(_request: Request, _exc: IntegrityError) -> JSONResponse:
        return error_response(
            code="CONFLICT",
            message=(
                "Resource conflict — the operation could not be completed due to a constraint "
                "violation"
            ),
            status_code=409,
        )

    @app.get("/health", tags=["health"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
