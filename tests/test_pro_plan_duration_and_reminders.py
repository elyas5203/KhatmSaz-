"""Unit tests for 30-day PRO plan duration, additive renewals, and expiration reminders."""

import math
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from khatmsaz.modules.plan import repository, service
from khatmsaz.modules.plan.models import PlanTier, UserPlan
from khatmsaz.modules.plan.service import (
    get_plan,
    get_plan_details,
    purchase_pro_plan,
    process_plan_expirations_and_reminders,
)


@pytest.mark.asyncio
async def test_purchase_pro_plan_sets_30_days(monkeypatch):
    user_id = uuid4()
    pro_def = SimpleNamespace(title="پرو", enabled=True, price_toman=50_000)
    monkeypatch.setattr(service, "get_definition", AsyncMock(return_value=pro_def))
    monkeypatch.setattr(service.wallet_service, "purchase", AsyncMock(return_value=SimpleNamespace()))

    mock_row = None
    async def mock_extend(session, uid, days=30):
        nonlocal mock_row
        now = datetime.now(timezone.utc)
        mock_row = UserPlan(
            user_id=uid,
            plan=PlanTier.PRO,
            starts_at=now,
            expires_at=now + timedelta(days=days),
            reminded_7d=False,
            reminded_24h=False,
            expired_notified=False,
        )
        return mock_row, mock_row.expires_at

    monkeypatch.setattr(repository, "get_by_user", AsyncMock(return_value=None))
    monkeypatch.setattr(repository, "extend_pro_plan", mock_extend)

    invoice, new_expiry = await purchase_pro_plan(object(), user_id, days=30)
    assert new_expiry is not None
    now = datetime.now(timezone.utc)
    diff_days = (new_expiry - now).total_seconds() / 86400
    assert 29.9 <= diff_days <= 30.1


@pytest.mark.asyncio
async def test_renew_active_pro_plan_adds_30_days_additively(monkeypatch):
    """If user has 10 days remaining on PRO, renewing adds 30 days to equal 40 days."""
    user_id = uuid4()
    now = datetime.now(timezone.utc)
    existing_expiry = now + timedelta(days=10)
    existing_row = UserPlan(
        user_id=user_id,
        plan=PlanTier.PRO,
        starts_at=now - timedelta(days=20),
        expires_at=existing_expiry,
        reminded_7d=False,
        reminded_24h=False,
        expired_notified=False,
    )

    pro_def = SimpleNamespace(title="پرو", enabled=True, price_toman=50_000)
    monkeypatch.setattr(service, "get_definition", AsyncMock(return_value=pro_def))
    monkeypatch.setattr(service.wallet_service, "purchase", AsyncMock(return_value=SimpleNamespace()))

    async def mock_extend(session, uid, days=30):
        new_expiry = existing_row.expires_at + timedelta(days=days)
        existing_row.expires_at = new_expiry
        existing_row.reminded_7d = False
        existing_row.reminded_24h = False
        existing_row.expired_notified = False
        return existing_row, new_expiry

    monkeypatch.setattr(repository, "get_by_user", AsyncMock(return_value=existing_row))
    monkeypatch.setattr(repository, "extend_pro_plan", mock_extend)

    invoice, new_expiry = await purchase_pro_plan(object(), user_id, days=30)
    diff_days = (new_expiry - now).total_seconds() / 86400
    assert 39.9 <= diff_days <= 40.1


@pytest.mark.asyncio
async def test_get_plan_lazy_expiration():
    """An expired PRO plan evaluates lazily to FREE (or BASIC if past cap)."""
    user_id = uuid4()
    now = datetime.now(timezone.utc)

    # Active PRO plan
    active_row = SimpleNamespace(
        plan=PlanTier.PRO,
        expires_at=now + timedelta(days=5),
    )
    # Expired PRO plan
    expired_row = SimpleNamespace(
        plan=PlanTier.PRO,
        expires_at=now - timedelta(seconds=10),
    )

    # Test active
    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=active_row)
    assert await get_plan(mock_session, user_id) == PlanTier.PRO

    # Test expired with small audience (< cap)
    mock_session.get = AsyncMock(return_value=expired_row)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(service, "get_free_total_member_cap", AsyncMock(return_value=1000))
        mp.setattr(service, "count_total_active_members", AsyncMock(return_value=50))
        assert await get_plan(mock_session, user_id) == PlanTier.FREE

    # Test expired with large audience (> cap)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(service, "get_free_total_member_cap", AsyncMock(return_value=1000))
        mp.setattr(service, "count_total_active_members", AsyncMock(return_value=1500))
        assert await get_plan(mock_session, user_id) == PlanTier.BASIC


@pytest.mark.asyncio
async def test_get_plan_details_calculates_remaining_days():
    user_id = uuid4()
    now = datetime.now(timezone.utc)
    active_row = SimpleNamespace(
        plan=PlanTier.PRO,
        expires_at=now + timedelta(days=14, hours=2),
    )
    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=active_row)

    details = await get_plan_details(mock_session, user_id)
    assert details["plan"] == PlanTier.PRO
    assert details["days_left"] == 15


@pytest.mark.asyncio
async def test_process_plan_expirations_and_reminders_flow(monkeypatch):
    """Tests 7-day warnings, 24-hour warnings, and lapse downgrades."""
    now = datetime.now(timezone.utc)
    u_7d = uuid4()
    u_24h = uuid4()
    u_expired = uuid4()

    row_7d = SimpleNamespace(user_id=u_7d, plan=PlanTier.PRO, expires_at=now + timedelta(days=6), reminded_7d=False)
    row_24h = SimpleNamespace(user_id=u_24h, plan=PlanTier.PRO, expires_at=now + timedelta(hours=18), reminded_24h=False)
    row_exp = SimpleNamespace(user_id=u_expired, plan=PlanTier.PRO, expires_at=now - timedelta(hours=1), expired_notified=False)

    monkeypatch.setattr(repository, "list_needing_7d_reminder", AsyncMock(return_value=[row_7d]))
    monkeypatch.setattr(repository, "list_needing_24h_reminder", AsyncMock(return_value=[row_24h]))
    monkeypatch.setattr(repository, "list_newly_expired_pro", AsyncMock(return_value=[row_exp]))

    mark_7d = AsyncMock()
    mark_24h = AsyncMock()
    downgrade = AsyncMock()
    monkeypatch.setattr(repository, "mark_7d_reminded", mark_7d)
    monkeypatch.setattr(repository, "mark_24h_reminded", mark_24h)
    monkeypatch.setattr(repository, "downgrade_expired_pro", downgrade)

    monkeypatch.setattr(service, "get_free_total_member_cap", AsyncMock(return_value=1000))
    monkeypatch.setattr(service, "count_total_active_members", AsyncMock(return_value=200))

    mock_identity = SimpleNamespace(platform=SimpleNamespace(value="telegram"), subject="12345")
    monkeypatch.setattr(
        "khatmsaz.modules.identity.service.list_identities_for_user",
        AsyncMock(return_value=[mock_identity]),
    )

    sent_notifications = []
    async def mock_notify(platform, subject, text):
        sent_notifications.append((platform, subject, text))

    test_session = object()
    counts = await process_plan_expirations_and_reminders(test_session, mock_notify)

    assert counts["reminded_7d"] == 1
    assert counts["reminded_24h"] == 1
    assert counts["expired"] == 1

    mark_7d.assert_awaited_once_with(test_session, u_7d)
    mark_24h.assert_awaited_once_with(test_session, u_24h)
    downgrade.assert_awaited_once_with(test_session, u_expired, PlanTier.FREE)

    assert len(sent_notifications) == 3
    # Verify 7d text
    assert "۷ روز تا پایان اعتبار" in sent_notifications[0][2]
    # Verify 24h text
    assert "تنها ۲۴ ساعت" in sent_notifications[1][2]
    # Verify expired text
    assert "مهلت ۳۰ روزه پلن حرفه‌ای شما به پایان رسید" in sent_notifications[2][2]
