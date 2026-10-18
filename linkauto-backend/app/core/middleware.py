"""HTTP middleware: security headers on every response, and a cap on request body size."""

from typing import TYPE_CHECKING, override

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.schemas.common import error_response

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response
    from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add hardening headers (nosniff, frame denial, referrer/permissions policy, no-cache)."""

    @override
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Call the next handler and set the security headers on its response."""
        response = await call_next(request)

        # D04: Injetar cabeçalhos de segurança recomendados (SECURITY_TECHNIQUES.md)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"

        return response


class _BodyTooLargeError(Exception):
    """The request body went past the limit while it was being received."""


class MaxBodySizeMiddleware:
    """Answer 413 to request bodies larger than ``max_bytes``, before the app buffers them.

    A declared ``Content-Length`` over the limit is rejected right away; bodies without one
    (chunked) are counted as they arrive and cut off once they pass the limit.
    """

    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        """Wrap ``app`` and store the limit in bytes."""
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Pass the request through, or answer 413 when its body is too large."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if self._declared_length(scope) > self.max_bytes:
            await self._reject(scope, receive, send)
            return

        received = 0
        response_started = False

        async def counting_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    raise _BodyTooLargeError
            return message

        async def tracking_send(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, counting_receive, tracking_send)
        except _BodyTooLargeError:
            if not response_started:
                await self._reject(scope, receive, send)

    @staticmethod
    def _declared_length(scope: Scope) -> int:
        for name, value in scope.get("headers", []):
            if name == b"content-length":
                try:
                    return int(value)
                except ValueError:
                    return 0
        return 0

    async def _reject(self, scope: Scope, receive: Receive, send: Send) -> None:
        response = error_response(
            code="PAYLOAD_TOO_LARGE",
            message=f"Request body exceeds {self.max_bytes // (1024 * 1024)} MB.",
            status_code=413,
        )
        await response(scope, receive, send)
