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

from limits import RateLimitItem, parse
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
# Password reset e-mails per account, so a victim's inbox can't be flooded by rotating IPs
PASSWORD_RESET_ACCOUNT_LIMIT = "3/hour"  # noqa: S105 - a rate limit, not a password
_password_reset_account_limit = parse(PASSWORD_RESET_ACCOUNT_LIMIT)
# Credential document uploads per user (each one stores two files of up to 10 MB)
UPLOAD_LIMIT = "10/hour"
_upload_limit = parse(UPLOAD_LIMIT)
# Booking messages per sender (each one e-mails the other participant)
MESSAGE_LIMIT = "20/minute"
_message_limit = parse(MESSAGE_LIMIT)


def _hit_or_raise(limit: RateLimitItem, namespace: str, key: str, scope: str) -> None:
    """Count one hit on the shared storage; raise ``RateLimitExceeded`` (429) if over."""
    if not limiter.enabled:
        return
    if not limiter.limiter.hit(limit, namespace, key):
        raise RateLimitExceeded(
            Limit(
                limit,
                key_func=lambda: key,
                scope=scope,
                per_method=False,
                methods=None,
                error_message=None,
                exempt_when=None,
                cost=1,
                override_defaults=False,
            )
        )


def check_login_account_limit(email: str) -> None:
    """Count a login attempt for the account; raise ``RateLimitExceeded`` (429) if over.

    Uses the limiter's shared storage, so the count is global across workers.
    """
    _hit_or_raise(_login_account_limit, "login", login_account_key(email), "login-account")


def check_message_limit(user_id: str) -> None:
    """Count a booking message sent by the user; raise ``RateLimitExceeded`` (429) if over.

    Per account, not per IP: every message e-mails the other participant, so a sender must
    not be able to flood an inbox by rotating IPs.
    """
    _hit_or_raise(_message_limit, "messages", f"user:{user_id}", "booking-messages")


def allow_password_reset_for(email: str) -> bool:
    """Count a password reset request for the account; ``False`` once over the limit.

    Callers skip over-limit requests silently (still answering 202), so the response never
    reveals whether the account exists or was rate limited.
    """
    if not limiter.enabled:
        return True
    return limiter.limiter.hit(
        _password_reset_account_limit, "password-reset", login_account_key(email)
    )


def check_upload_limit(user_id: str) -> None:
    """Count a document upload by the user; raise ``RateLimitExceeded`` (429) if over."""
    _hit_or_raise(_upload_limit, "uploads", f"user:{user_id}", "document-uploads")
