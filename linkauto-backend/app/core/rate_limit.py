"""Shared slowapi rate limiter: client-IP and per-account limits on shared storage.

Counters live in ``RATE_LIMIT_STORAGE_URI``. Redis is optional: with ``redis://...`` every
worker and replica shares the same limits; with the default ``memory://`` each process
counts on its own. The client IP is ``request.client.host``,
which reflects the real client only when the app runs behind a trusted proxy configured
in ``TRUSTED_PROXIES`` (see ``ProxyHeadersMiddleware`` in ``app.main``).
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from limits import parse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.wrappers import Limit

from app.core.config import get_settings

if TYPE_CHECKING:
    from starlette.requests import Request

    from app.core.config import Settings


def client_ip(request: Request) -> str:
    """Return the caller's IP (already resolved through trusted proxies), or ``unknown``."""
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def login_account_key(email: str) -> str:
    """Return the rate-limit key for an account: a hash of its normalized e-mail."""
    digest = hashlib.sha256(email.strip().lower().encode()).hexdigest()[:32]
    return f"account:{digest}"


def trusted_proxy_middleware_hosts(settings: Settings) -> list[str] | None:
    """Return the IPs/CIDRs whose ``X-Forwarded-For`` is trusted, or None when unset."""
    hosts = [host.strip() for host in settings.trusted_proxies.split(",") if host.strip()]
    return hosts or None


def build_limiter(settings: Settings) -> Limiter:
    """Create the limiter keyed by client IP on the configured storage."""
    return Limiter(
        key_func=client_ip,
        storage_uri=settings.rate_limit_storage_uri,
        # Keep serving if the shared storage is briefly unreachable (per-process limits)
        in_memory_fallback_enabled=settings.rate_limit_storage_uri != "memory://",
        key_prefix="linkauto",
    )


limiter = build_limiter(get_settings())

# Attempts allowed per account (normalized e-mail), whatever the client IP
LOGIN_ACCOUNT_LIMIT = "10/15 minutes"
_login_account_limit = parse(LOGIN_ACCOUNT_LIMIT)


def check_login_account_limit(email: str) -> None:
    """Count a login attempt for the account; raise ``RateLimitExceeded`` (429) if over.

    Uses the limiter's shared storage, so the count is global across workers.
    """
    if not limiter.enabled:
        return
    if not limiter.limiter.hit(_login_account_limit, "login", login_account_key(email)):
        raise RateLimitExceeded(
            Limit(
                _login_account_limit,
                key_func=lambda: login_account_key(email),
                scope="login-account",
                per_method=False,
                methods=None,
                error_message=None,
                exempt_when=None,
                cost=1,
                override_defaults=False,
            )
        )
