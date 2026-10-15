"""Tests for MASTER-10:
- Broadcast 1,000-recipient tier pricing & PRO requirement
- Wallet receipt upload, approval & rejection lifecycle
- Creator panel admin-only guard in bot and web app
"""

import math
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from khatmsaz.modules.broadcast.models import BroadcastStatus, KhatmBroadcast
from khatmsaz.modules.broadcast import service as broadcast_service
from khatmsaz.modules.identity.models import UserRole
from khatmsaz.modules.plan.models import PlanTier
from khatmsaz.modules.wallet.models import ReceiptClaimStatus, WalletReceiptClaim
from khatmsaz.modules.wallet import service as wallet_service


# -----------------------------------------------------------------------------
# 1. Broadcast 1,000-Recipient Tier Pricing Tests
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_broadcast_allows_any_plan_if_funded(monkeypatch):
    """MASTER-31: Basic and Free plan creators can submit broadcasts as long as wallet covers cost."""
    session = AsyncMock()
    creator_id = uuid4()

    monkeypatch.setattr(
        broadcast_service,
        "audience_user_ids",
        AsyncMock(return_value=[uuid4() for _ in range(50)]),
    )
    monkeypatch.setattr(
        broadcast_service,
        "channel_policy",
        AsyncMock(return_value=(0, 50_000, 1000)),
    )
    mock_spend = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.wallet.service.spend", mock_spend)
    monkeypatch.setattr(
        "khatmsaz.modules.broadcast.repository.create",
        AsyncMock(return_value=SimpleNamespace(id=uuid4(), cost_toman=50_000)),
    )

    res = await broadcast_service.submit(
        session,
        khatm_id=None,
        creator_user_id=creator_id,
        body="پیام آزمایشی",
        channel="TELEGRAM",
    )
    assert res is not None
    assert mock_spend.await_count == 1


@pytest.mark.asyncio
async def test_broadcast_1000_recipient_tier_calculation(monkeypatch):
    """
    1 to 1000 recipients = 1 package (50,000 Toman)
    1001 to 2000 recipients = 2 packages (100,000 Toman)
    6000 recipients = 6 packages (300,000 Toman)
    """
    session = AsyncMock()
    creator_id = uuid4()

    monkeypatch.setattr(
        "khatmsaz.modules.plan.service.get_plan",
        AsyncMock(return_value=PlanTier.PRO),
    )
    monkeypatch.setattr(
        broadcast_service,
        "channel_policy",
        AsyncMock(return_value=(0, 50_000)),
    )
    mock_spend = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.wallet.service.spend", mock_spend)
    mock_create = AsyncMock(return_value=SimpleNamespace(id=uuid4(), cost_toman=0))
    monkeypatch.setattr("khatmsaz.modules.broadcast.repository.create", mock_create)

    # Case A: 500 recipients -> 1 package -> 50,000 Toman
    monkeypatch.setattr(
        broadcast_service,
        "audience_user_ids",
        AsyncMock(return_value=[uuid4() for _ in range(500)]),
    )
    await broadcast_service.submit(
        session, khatm_id=None, creator_user_id=creator_id, body="تست ۵۰۰ نفر", channel="TELEGRAM"
    )
    mock_spend.assert_awaited_with(
        session,
        user_id=creator_id,
        amount=50_000,
        description="هزینه ارسال پیام گروهی (1 بسته ۱۰۰۰ نفری برای 500 مخاطب)",
        invoice_kind=pytest.approx(broadcast_service.InvoiceKind.PURCHASE),
    )

    # Case B: 1001 recipients -> 2 packages -> 100,000 Toman
    monkeypatch.setattr(
        broadcast_service,
        "audience_user_ids",
        AsyncMock(return_value=[uuid4() for _ in range(1001)]),
    )
    await broadcast_service.submit(
        session, khatm_id=None, creator_user_id=creator_id, body="تست ۱۰۰۱ نفر", channel="TELEGRAM"
    )
    mock_spend.assert_awaited_with(
        session,
        user_id=creator_id,
        amount=100_000,
        description="هزینه ارسال پیام گروهی (2 بسته ۱۰۰۰ نفری برای 1001 مخاطب)",
        invoice_kind=pytest.approx(broadcast_service.InvoiceKind.PURCHASE),
    )

    # Case C: 6000 recipients -> 6 packages -> 300,000 Toman
    monkeypatch.setattr(
        broadcast_service,
        "audience_user_ids",
        AsyncMock(return_value=[uuid4() for _ in range(6000)]),
    )
    await broadcast_service.submit(
        session, khatm_id=None, creator_user_id=creator_id, body="تست ۶۰۰۰ نفر", channel="TELEGRAM"
    )
    mock_spend.assert_awaited_with(
        session,
        user_id=creator_id,
        amount=300_000,
        description="هزینه ارسال پیام گروهی (6 بسته ۱۰۰۰ نفری برای 6000 مخاطب)",
        invoice_kind=pytest.approx(broadcast_service.InvoiceKind.PURCHASE),
    )


@pytest.mark.asyncio
async def test_broadcast_rejection_refunds_wallet(monkeypatch):
    """If a broadcast is rejected during moderation, its cost is refunded."""
    session = AsyncMock()
    creator_id = uuid4()
    bc_id = uuid4()
    mock_item = SimpleNamespace(
        id=bc_id,
        creator_user_id=creator_id,
        cost_toman=150_000,
        status=BroadcastStatus.PENDING,
    )

    monkeypatch.setattr(
        "khatmsaz.modules.broadcast.repository.get_by_id",
        AsyncMock(return_value=mock_item),
    )
    monkeypatch.setattr(
        "khatmsaz.modules.broadcast.repository.mark_reviewed",
        AsyncMock(),
    )
    mock_add_cash = AsyncMock()
    monkeypatch.setattr("khatmsaz.modules.wallet.service.add_cash", mock_add_cash)
    monkeypatch.setattr(
        "khatmsaz.modules.wallet.service.refund_purchase_invoice",
        AsyncMock(return_value=None),
    )

    await broadcast_service.reject(session, bc_id, note="عدم رعایت محتوا")

    mock_add_cash.assert_awaited_once_with(
        session,
        user_id=creator_id,
        amount=150_000,
        description=f"بازگشت وجه پیام گروهی رد شده (کد: {str(bc_id)[:8]})",
        ref=f"REFUND-BC-{str(bc_id)[:8]}",
    )


# -----------------------------------------------------------------------------
# 2. Bank Receipt Top-Up Flow Tests
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_wallet_receipt_claim_lifecycle(monkeypatch):
    """Submit, approve and reject receipt claims."""
    session = AsyncMock()
    user_id = uuid4()
    admin_id = uuid4()
    claim_id = uuid4()

    mock_claim = WalletReceiptClaim(
        id=claim_id,
        user_id=user_id,
        amount_toman=100_000,
        photo_file_id="photo_xyz",
        status=ReceiptClaimStatus.PENDING.value,
    )

    # 1. Submit
    monkeypatch.setattr(
        "khatmsaz.modules.wallet.repository.create_receipt_claim",
        AsyncMock(return_value=mock_claim),
    )
    claim = await wallet_service.submit_receipt_claim(
        session,
        user_id=user_id,
        amount_toman=100_000,
        photo_file_id="photo_xyz",
    )
    assert claim.amount_toman == 100_000
    assert claim.status == ReceiptClaimStatus.PENDING.value

    # 2. Approve
    approved_claim = WalletReceiptClaim(
        id=claim_id,
        user_id=user_id,
        amount_toman=100_000,
        photo_file_id="photo_xyz",
        status=ReceiptClaimStatus.APPROVED.value,
        admin_user_id=admin_id,
    )
    monkeypatch.setattr(
        "khatmsaz.modules.wallet.repository.review_receipt_claim",
        AsyncMock(return_value=approved_claim),
    )
    mock_add_cash = AsyncMock(return_value=SimpleNamespace(id=uuid4()))
    monkeypatch.setattr(wallet_service, "add_cash", mock_add_cash)

    c, inv = await wallet_service.approve_receipt_claim(
        session,
        claim_id=claim_id,
        admin_user_id=admin_id,
    )
    assert c.status == ReceiptClaimStatus.APPROVED.value
    mock_add_cash.assert_awaited_once_with(
        session,
        user_id,
        100_000,
        description=f"شارژ کیف پول با فیش واریزی (کد: {str(claim_id)[:8]})",
        ref=f"RECEIPT-{str(claim_id)[:8]}",
    )

    # 3. Reject
    rejected_claim = WalletReceiptClaim(
        id=claim_id,
        user_id=user_id,
        amount_toman=100_000,
        photo_file_id="photo_xyz",
        status=ReceiptClaimStatus.REJECTED.value,
        admin_user_id=admin_id,
    )
    monkeypatch.setattr(
        "khatmsaz.modules.wallet.repository.review_receipt_claim",
        AsyncMock(return_value=rejected_claim),
    )
    r = await wallet_service.reject_receipt_claim(
        session,
        claim_id=claim_id,
        admin_user_id=admin_id,
        admin_note="فیش ناخوانا",
    )
    assert r.status == ReceiptClaimStatus.REJECTED.value


# -----------------------------------------------------------------------------
# 3. Creator Panel Admin Guard Tests
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_creator_web_login_bot_command_guards_non_admins(monkeypatch):
    """Non-admin sending /creator_panel gets the friendly under-update message."""
    from khatmsaz.bot.handlers.my_khatms import creator_web_login

    message = MagicMock()
    message.chat = SimpleNamespace(id=99999)
    message.answer = AsyncMock()
    message.bot = MagicMock()
    message.bot.khatmsaz_platform = "telegram"

    # Mock _lang_for to avoid DB lookup
    monkeypatch.setattr(
        "khatmsaz.bot.handlers.my_khatms._lang_for",
        AsyncMock(return_value="fa"),
    )

    # Non-admin user (UserRole.CREATOR)
    mock_user = SimpleNamespace(id=uuid4(), role=UserRole.CREATOR)
    monkeypatch.setattr(
        "khatmsaz.modules.identity.service.find_by_platform",
        AsyncMock(return_value=mock_user),
    )
    monkeypatch.setattr(
        "khatmsaz.bot.handlers.my_khatms.get_settings",
        lambda: SimpleNamespace(admin_web_base_url="https://app.khatmsaz.com"),
    )

    await creator_web_login(message)

    message.answer.assert_awaited_once()
    sent_text = message.answer.await_args[0][0]
    assert "در دست به‌روزرسانی و ارتقا می‌باشد" in sent_text


@pytest.mark.asyncio
async def test_creator_panel_keyboard_hides_mini_app_from_non_admins():
    """In bot panel keyboard, mini app button is hidden when is_admin is False."""
    from khatmsaz.bot.handlers.panel import creator_panel_keyboard

    # Non-admin
    kb_user = creator_panel_keyboard("fa", is_admin=False)
    all_callbacks_user = [
        btn.callback_data
        for row in kb_user.inline_keyboard
        for btn in row
        if btn.callback_data
    ]
    assert "creator:web_login" not in all_callbacks_user

    # Admin - in MASTER-19, creator:web_login is hidden per user request
    kb_admin = creator_panel_keyboard("fa", is_admin=True)
    all_callbacks_admin = [
        btn.callback_data
        for row in kb_admin.inline_keyboard
        for btn in row
        if btn.callback_data
    ]
    assert "creator:web_login" not in all_callbacks_admin
