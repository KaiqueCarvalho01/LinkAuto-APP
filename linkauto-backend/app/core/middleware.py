"""HTTP middleware that adds security headers to every response."""

from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add hardening headers (nosniff, frame denial, referrer/permissions policy, no-cache)."""

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
