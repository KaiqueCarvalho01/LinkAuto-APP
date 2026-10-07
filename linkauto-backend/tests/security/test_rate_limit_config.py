"""Rate limits use shared storage and the real client IP behind a trusted proxy (#26)."""

import logging
from typing import TYPE_CHECKING

from fastapi.testclient import TestClient
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.core.config import Settings
from app.core.rate_limit import (
    build_limiter,
    client_ip,
    login_account_key,
    trusted_proxy_middleware_hosts,
)
from app.main import create_app

if TYPE_CHECKING:
    import pytest


def test_limiter_uses_configured_shared_storage() -> None:
    limiter = build_limiter(Settings(RATE_LIMIT_STORAGE_URI="memory://"))
    assert limiter._storage_uri == "memory://"  # noqa: SLF001


def test_production_starts_without_redis_and_warns(caplog: pytest.LogCaptureFixture) -> None:
    """Redis is optional: without it, limits are counted per process (with a warning)."""
    with caplog.at_level(logging.WARNING):
        settings = Settings(
            APP_ENV="production", JWT_SECRET="secure", RESET_SQLITE_ON_STARTUP=False
        )

    assert settings.rate_limit_storage_uri == "memory://"
    assert any("RATE_LIMIT_STORAGE_URI" in message for message in caplog.messages)


def test_development_without_redis_does_not_warn(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING):
        Settings(APP_ENV="development")

    assert not any("RATE_LIMIT_STORAGE_URI" in message for message in caplog.messages)


def test_trusted_proxies_default_to_none() -> None:
    assert trusted_proxy_middleware_hosts(Settings()) is None
    assert trusted_proxy_middleware_hosts(Settings(TRUSTED_PROXIES="10.0.0.0/8, 10.1.2.3")) == [
        "10.0.0.0/8",
        "10.1.2.3",
    ]


def _app_with_proxy(trusted: str) -> TestClient:
    app = create_app(Settings(TRUSTED_PROXIES=trusted))
    return TestClient(app, client=("10.0.0.5", 50000))


def test_x_forwarded_for_is_honoured_only_from_trusted_proxies() -> None:
    trusted = _app_with_proxy("10.0.0.0/8")
    resp = trusted.get("/api/v1/foundation/whoami", headers={"X-Forwarded-For": "203.0.113.7"})
    assert resp.json()["data"]["client_ip"] == "203.0.113.7"

    untrusted = _app_with_proxy("192.168.0.1")
    resp = untrusted.get("/api/v1/foundation/whoami", headers={"X-Forwarded-For": "203.0.113.7"})
    assert resp.json()["data"]["client_ip"] == "10.0.0.5"


def test_proxy_middleware_is_installed_only_when_configured() -> None:
    def has_proxy_middleware(settings: Settings) -> bool:
        return any(m.cls is ProxyHeadersMiddleware for m in create_app(settings).user_middleware)

    assert has_proxy_middleware(Settings(TRUSTED_PROXIES="10.0.0.1"))
    assert not has_proxy_middleware(Settings())


def test_login_is_also_limited_per_account(client: TestClient) -> None:
    """Rotating client IPs doesn't help a brute force against one account."""
    app = client.app
    for i in range(10):
        attacker = TestClient(app, client=(f"198.51.100.{i}", 50000))
        resp = attacker.post(
            "/api/v1/auth/login", json={"email": "Victim@x.com", "password": "wrong"}
        )
        assert resp.status_code == 401

    # Same account (case/space-insensitive) from yet another IP: per-account limit applies
    fresh = TestClient(app, client=("198.51.100.200", 50000))
    resp = fresh.post("/api/v1/auth/login", json={"email": " victim@x.com", "password": "x"})
    assert resp.status_code == 429
    assert resp.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    # Other accounts from that IP are unaffected
    other = fresh.post("/api/v1/auth/login", json={"email": "other@x.com", "password": "x"})
    assert other.status_code == 401


def test_login_account_key_normalizes_email() -> None:
    assert login_account_key(" Victim@X.com ") == login_account_key("victim@x.com")
    assert "victim" not in login_account_key("victim@x.com")  # hashed, not logged in clear


def test_client_ip_falls_back_when_unknown() -> None:
    from starlette.requests import Request  # noqa: PLC0415

    assert client_ip(Request({"type": "http", "headers": [], "client": None})) == "unknown"
