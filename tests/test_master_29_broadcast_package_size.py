"""Tests for MASTER-29: Broadcast Dynamic Package Size & Ad Reward Rate UI Removal."""

import math
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from starlette.requests import Request

from khatmsaz.modules.broadcast import service as broadcast_service
from khatmsaz.modules.identity.models import User, UserRole
from khatmsaz.modules.plan.models import PlanTier
from khatmsaz.modules.system_settings import service as system_settings_service


# --- 1. System Settings Package Size Keys ---

@pytest.mark.asyncio
async def test_system_settings_broadcast_package_size_keys():
    """Verify system_settings service recognizes broadcast package size keys."""
    for ch in ("telegram", "bale", "sms"):
        key = f"broadcast_{ch}_package_size"
        assert key in system_settings_service.KNOWN_SETTINGS
        assert system_settings_service.KNOWN_SETTINGS[key]["default"] == 1000
        assert system_settings_service.KNOWN_SETTINGS[key]["min"] == 1


# --- 2. Broadcast Channel Policy & Package Size ---

@pytest.mark.asyncio
async def test_channel_policy_and_package_size():
    """Verify channel_policy returns (free_count, price_toman) and channel_package_size returns custom size."""
    mock_session = AsyncMock()

    with patch("khatmsaz.modules.system_settings.service.get_int") as mock_get_int:
        async def side_effect(session, key):
            if "free_count" in key:
                return 0
            if "price_toman" in key:
                return 60_000
            if "package_size" in key:
                return 7374
            return 1000

        mock_get_int.side_effect = side_effect

        policy = await broadcast_service.channel_policy(mock_session, "TELEGRAM")
        assert policy == (0, 60_000)

        package_size = await broadcast_service.channel_package_size(mock_session, "TELEGRAM")
        assert package_size == 7374


# --- 3. Dynamic Package Size Calculation in submit() ---

@pytest.mark.asyncio
async def test_broadcast_submit_custom_package_size_100():
    """Verify that submit calculates packages count using custom package_size (e.g. 100)."""
    mock_session = AsyncMock()
    creator_id = uuid4()
    # 250 audience members
    audience = [uuid4() for _ in range(250)]

    with patch("khatmsaz.modules.broadcast.service.audience_user_ids", new=AsyncMock(return_value=audience)), \
         patch("khatmsaz.modules.plan.service.get_plan", new=AsyncMock(return_value=PlanTier.PRO)), \
         patch("khatmsaz.modules.broadcast.service.channel_policy", new=AsyncMock(return_value=(0, 10_000, 100))), \
         patch("khatmsaz.modules.wallet.service.spend", new=AsyncMock(return_value=None)) as mock_spend, \
         patch("khatmsaz.modules.broadcast.repository.create", new=AsyncMock()) as mock_create:

        await broadcast_service.submit(
            mock_session,
            khatm_id=None,
            creator_user_id=creator_id,
            body="تست پیام گروهی با بسته ۱۰۰ تایی",
            channel="TELEGRAM",
        )

        # 250 / 100 = 2.5 -> 3 packages
        # 3 * 10,000 = 30,000 Toman
        mock_spend.assert_awaited_once()
        spend_kwargs = mock_spend.call_args.kwargs
        assert spend_kwargs["amount"] == 30_000
        assert "3 بسته 100 نفری" in spend_kwargs["description"] or "3 بسته ۱۰۰ نفری" in spend_kwargs["description"]


@pytest.mark.asyncio
async def test_broadcast_submit_custom_package_size_7374():
    """Verify that submit calculates packages count using custom package_size (e.g. 7374)."""
    mock_session = AsyncMock()
    creator_id = uuid4()
    # 7375 audience members -> exactly 2 packages with size 7374
    audience = [uuid4() for _ in range(7375)]

    with patch("khatmsaz.modules.broadcast.service.audience_user_ids", new=AsyncMock(return_value=audience)), \
         patch("khatmsaz.modules.plan.service.get_plan", new=AsyncMock(return_value=PlanTier.PRO)), \
         patch("khatmsaz.modules.broadcast.service.channel_policy", new=AsyncMock(return_value=(0, 200_000, 7374))), \
         patch("khatmsaz.modules.wallet.service.spend", new=AsyncMock(return_value=None)) as mock_spend, \
         patch("khatmsaz.modules.broadcast.repository.create", new=AsyncMock()):

        await broadcast_service.submit(
            mock_session,
            khatm_id=None,
            creator_user_id=creator_id,
            body="تست پیام گروهی با بسته ۷۳۷۴ تایی",
            channel="TELEGRAM",
        )

        mock_spend.assert_awaited_once()
        spend_kwargs = mock_spend.call_args.kwargs
        # 7375 / 7374 -> ceil = 2 packages
        assert spend_kwargs["amount"] == 400_000
        assert "2 بسته" in spend_kwargs["description"]


# --- 4. Web Admin Endpoint for Setting Package Size ---

@pytest.mark.asyncio
async def test_web_admin_update_broadcast_policy_saves_package_size():
    """Verify POST /finance/broadcast-policy saves package_size in system_settings."""
    from khatmsaz.web.app import update_broadcast_policy

    mock_request = AsyncMock(spec=Request)
    mock_admin = User(id=uuid4(), role=UserRole.SUPER_ADMIN)

    with patch("khatmsaz.web.app._admin", new=AsyncMock(return_value=(mock_admin, {"csrf": "token"}))), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope") as mock_scope, \
         patch("khatmsaz.web.app.system_settings_service.set_int", new=AsyncMock()) as mock_set_int, \
         patch("khatmsaz.web.app.audit_service.record", new=AsyncMock()):

        mock_session = AsyncMock()
        mock_scope.return_value.__aenter__.return_value = mock_session

        resp = await update_broadcast_policy(
            request=mock_request,
            csrf="token",
            channel="TELEGRAM",
            price_toman=75_000,
            package_size=500,
            free_count=0,
        )

        assert resp.status_code == 303
        assert "/finance?saved=broadcast_policy" in resp.headers["location"]

        # Verify package_size was saved
        saved_keys = [call[0][1] for call in mock_set_int.call_args_list]
        saved_values = [call[0][2] for call in mock_set_int.call_args_list]

        assert "broadcast_telegram_package_size" in saved_keys
        idx = saved_keys.index("broadcast_telegram_package_size")
        assert saved_values[idx] == 500
