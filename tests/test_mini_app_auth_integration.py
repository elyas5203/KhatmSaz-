"""PostgreSQL + ASGI proof for Telegram Mini App admin authentication."""

from datetime import datetime, timezone
import hashlib
import hmac
import json
from urllib.parse import urlencode

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User, UserRole
from khatmsaz.modules.session.models import Session
from khatmsaz.web.app import COOKIE_NAME, app


def _signed_init_data(token: str, subject: int, timestamp: int) -> str:
    values = {
        "auth_date": str(timestamp),
        "query_id": "AAH-integration",
        "user": json.dumps({"id": subject, "first_name": "مدیر تست"}, separators=(",", ":")),
    }
    check = "\n".join(f"{key}={value}" for key, value in sorted(values.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    values["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(values)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_signed_telegram_admin_launch_sets_secure_scoped_cookie(monkeypatch):
    token = "123456:integration-mini-app-token"
    subject = 9988776655
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", token)
    get_settings.cache_clear()
    async with session_scope() as session:
        admin = await identity_service.resolve_or_provision_user(session, Platform.TELEGRAM, subject)
        admin.role = UserRole.SUPER_ADMIN
        admin_id = admin.id

    signed = _signed_init_data(token, subject, int(datetime.now(timezone.utc).timestamp()))
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="https://app.khatmsaz.com") as client:
            landing = await client.get("/mini/admin")
            assert landing.status_code == 200
            assert "telegram-web-app.js" in landing.text

            response = await client.post(
                "/mini/admin/auth", data={"init_data": signed}, follow_redirects=False
            )
            assert response.status_code == 303
            assert response.headers["location"] == "/"
            assert COOKIE_NAME in response.cookies
            cookie = response.headers["set-cookie"]
            assert "HttpOnly" in cookie and "Secure" in cookie and "SameSite=lax" in cookie

            forged = await client.post(
                "/mini/admin/auth", data={"init_data": signed.replace("9988776655", "1")}
            )
            assert forged.status_code == 401

            legacy = await client.get("/login?token=old-url-token", follow_redirects=False)
            assert legacy.status_code == 401
            assert COOKIE_NAME not in legacy.cookies
    finally:
        async with session_scope() as session:
            await session.execute(delete(Session).where(Session.user_id == admin_id))
            await session.execute(delete(PlatformIdentity).where(PlatformIdentity.user_id == admin_id))
            await session.execute(delete(User).where(User.id == admin_id))
        get_settings.cache_clear()
