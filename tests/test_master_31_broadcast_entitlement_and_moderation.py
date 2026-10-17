"""Tests for MASTER-31: Broadcast Entitlement (all funded plans), In-Bot Moderation with Photo & Inline Buttons, and Web Media Preview."""

import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, User as TgUser
from starlette.requests import Request
from starlette.responses import Response

from khatmsaz.bot.handlers.creator_broadcast import _notify_admins_of_broadcast_request
from khatmsaz.bot.handlers.admin_bot.handlers import (
    _safe_edit_admin_message,
    approve_broadcast_callback,
    reject_broadcast_callback,
)
from khatmsaz.modules.broadcast import service as broadcast_service
from khatmsaz.modules.broadcast.delivery import deliver_broadcast
from khatmsaz.modules.broadcast.models import BroadcastStatus, KhatmBroadcast
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.plan.models import PlanTier
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.web.app import broadcast_media_preview


# --- 1. Broadcast Entitlement: Any Plan Can Submit If Funded ---

@pytest.mark.asyncio
async def test_broadcast_submit_free_plan_funded():
    """Creators on FREE or BASIC plan can submit broadcasts as long as wallet has funds."""
    mock_session = AsyncMock()
    creator_id = uuid4()
    audience = [uuid4() for _ in range(150)]

    created_bc = SimpleNamespace(id=uuid4(), audience_count=150, cost_toman=50_000)

    with patch("khatmsaz.modules.broadcast.service.audience_user_ids", new=AsyncMock(return_value=audience)), \
         patch("khatmsaz.modules.broadcast.service.channel_policy", new=AsyncMock(return_value=(0, 50_000, 1000))), \
         patch("khatmsaz.modules.wallet.service.spend", new=AsyncMock(return_value=None)) as mock_spend, \
         patch("khatmsaz.modules.broadcast.repository.create", new=AsyncMock(return_value=created_bc)):

        item = await broadcast_service.submit(
            mock_session,
            khatm_id=None,
            creator_user_id=creator_id,
            body="پیام همگانی برای اعضا",
            channel="TELEGRAM",
        )

        assert item is created_bc
        mock_spend.assert_awaited_once()
        assert mock_spend.call_args.kwargs["amount"] == 50_000


@pytest.mark.asyncio
async def test_broadcast_submit_insufficient_funds_raises():
    """If creator wallet has insufficient funds, InsufficientFundsError is raised."""
    mock_session = AsyncMock()
    creator_id = uuid4()
    audience = [uuid4() for _ in range(500)]

    with patch("khatmsaz.modules.broadcast.service.audience_user_ids", new=AsyncMock(return_value=audience)), \
         patch("khatmsaz.modules.broadcast.service.channel_policy", new=AsyncMock(return_value=(0, 50_000, 1000))), \
         patch("khatmsaz.modules.wallet.service.spend", side_effect=wallet_service.InsufficientFundsError("موجودی ناکافی")):

        with pytest.raises(wallet_service.InsufficientFundsError):
            await broadcast_service.submit(
                mock_session,
                khatm_id=None,
                creator_user_id=creator_id,
                body="پیام بدون موجودی",
                channel="TELEGRAM",
            )


# --- 2. In-Bot Push Notification with Photo & Inline Buttons ---

@pytest.mark.asyncio
async def test_notify_admins_broadcast_with_photo():
    """A broadcast carrying a photo sends notify_super_admins_photo with inline buttons."""
    item = SimpleNamespace(
        id=uuid4(),
        body="متن پوستر تبلیغاتی ختم",
        media_type="photo",
        media_file_id_telegram="tg_photo_file_123",
        audience_count=850,
        cost_toman=50_000,
    )
    mock_source_bot = AsyncMock()

    with patch("khatmsaz.bot.handlers.creator_broadcast.notify_super_admins_photo", new=AsyncMock()) as mock_photo_notify:
        await _notify_admins_of_broadcast_request(
            item=item,
            creator_name="علی محمدی",
            scope_title="ختم صلوات همگانی",
            source_bot=mock_source_bot,
        )

        mock_photo_notify.assert_awaited_once()
        kwargs = mock_photo_notify.call_args.kwargs
        assert kwargs["photo_file_id"] == "tg_photo_file_123"
        assert kwargs["source_bot"] is mock_source_bot
        markup = kwargs["reply_markup"]
        assert isinstance(markup, InlineKeyboardMarkup)
        buttons = [btn for row in markup.inline_keyboard for btn in row]
        button_callbacks = [b.callback_data for b in buttons]
        assert f"admin_broadcast:approve:{item.id}" in button_callbacks
        assert f"admin_broadcast:reject:{item.id}" in button_callbacks


@pytest.mark.asyncio
async def test_notify_admins_broadcast_text_only():
    """A broadcast with text only sends notify_super_admins with inline buttons."""
    item = SimpleNamespace(
        id=uuid4(),
        body="اطلاعیه شروع ختم جدید",
        media_type=None,
        media_file_id_telegram=None,
        audience_count=300,
        cost_toman=50_000,
    )

    with patch("khatmsaz.bot.handlers.creator_broadcast.notify_super_admins", new=AsyncMock()) as mock_text_notify:
        await _notify_admins_of_broadcast_request(
            item=item,
            creator_name="فاطمه حسینی",
            scope_title="ختم سوره یس",
            source_bot=None,
        )

        mock_text_notify.assert_awaited_once()
        markup = mock_text_notify.call_args.kwargs["reply_markup"]
        assert isinstance(markup, InlineKeyboardMarkup)
        buttons = [btn for row in markup.inline_keyboard for btn in row]
        button_callbacks = [b.callback_data for b in buttons]
        assert f"admin_broadcast:approve:{item.id}" in button_callbacks
        assert f"admin_broadcast:reject:{item.id}" in button_callbacks


# --- 3. Admin Bot Callback Handlers & Safe Message Editing ---

@pytest.mark.asyncio
async def test_safe_edit_admin_message_photo_vs_text():
    """_safe_edit_admin_message calls edit_caption for photo messages, edit_text for text messages."""
    # Case A: Message has photo
    msg_photo = AsyncMock()
    msg_photo.photo = [MagicMock()]
    msg_photo.edit_caption = AsyncMock()
    msg_photo.edit_text = AsyncMock()
    msg_photo.answer = AsyncMock()
    await _safe_edit_admin_message(msg_photo, "تأیید شد")
    msg_photo.edit_caption.assert_awaited_once_with(caption="تأیید شد", reply_markup=None)

    # Case B: Message has no photo
    msg_text = AsyncMock()
    msg_text.photo = None
    msg_text.edit_caption = AsyncMock()
    msg_text.edit_text = AsyncMock()
    msg_text.answer = AsyncMock()
    await _safe_edit_admin_message(msg_text, "تأیید شد")
    msg_text.edit_text.assert_awaited_once_with(text="تأیید شد", reply_markup=None)


@pytest.mark.asyncio
async def test_admin_broadcast_approve_callback():
    """Admin approving a broadcast approves it in DB, dispatches delivery, and updates message."""
    bc_id = uuid4()
    mock_b = SimpleNamespace(id=bc_id, cost_toman=50_000)

    callback = AsyncMock(spec=CallbackQuery)
    callback.data = f"admin_broadcast:approve:{bc_id}"
    callback.from_user = SimpleNamespace(id=123456789)
    callback.message = AsyncMock()
    callback.message.photo = None
    callback.message.edit_caption = AsyncMock()
    callback.message.edit_text = AsyncMock()
    callback.message.answer = AsyncMock()

    admin_user = SimpleNamespace(id=uuid4(), role=UserRole.SUPER_ADMIN)

    with patch("khatmsaz.bot.handlers.admin_bot.handlers._is_super_admin", new=AsyncMock(return_value=True)), \
         patch("khatmsaz.modules.identity.service.find_by_platform", new=AsyncMock(return_value=admin_user)), \
         patch("khatmsaz.modules.broadcast.service.approve", new=AsyncMock(return_value=mock_b)), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.deliver_broadcast", new=AsyncMock(return_value=150)) as mock_deliver, \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.safe_answer_callback", new=AsyncMock()):

        await approve_broadcast_callback(callback)

        mock_deliver.assert_awaited_once()
        callback.message.edit_text.assert_awaited_once()
        assert "150 مخاطب" in callback.message.edit_text.call_args.kwargs["text"]


@pytest.mark.asyncio
async def test_admin_broadcast_reject_callback():
    """Admin rejecting a broadcast rejects it in DB (triggering refund) and updates message."""
    bc_id = uuid4()
    mock_b = SimpleNamespace(id=bc_id, cost_toman=50_000)

    callback = AsyncMock(spec=CallbackQuery)
    callback.data = f"admin_broadcast:reject:{bc_id}"
    callback.from_user = SimpleNamespace(id=123456789)
    callback.message = AsyncMock()
    callback.message.photo = [MagicMock()]
    callback.message.edit_caption = AsyncMock()
    callback.message.edit_text = AsyncMock()
    callback.message.answer = AsyncMock()

    admin_user = SimpleNamespace(id=uuid4(), role=UserRole.SUPER_ADMIN)

    with patch("khatmsaz.bot.handlers.admin_bot.handlers._is_super_admin", new=AsyncMock(return_value=True)), \
         patch("khatmsaz.modules.identity.service.find_by_platform", new=AsyncMock(return_value=admin_user)), \
         patch("khatmsaz.modules.broadcast.service.reject", new=AsyncMock(return_value=mock_b)) as mock_reject, \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.safe_answer_callback", new=AsyncMock()):

        await reject_broadcast_callback(callback)

        mock_reject.assert_awaited_once()
        callback.message.edit_caption.assert_awaited_once()
        assert "50,000 تومان" in callback.message.edit_caption.call_args.kwargs["caption"]


# --- 4. Web Media Preview Endpoint ---

@pytest.mark.asyncio
async def test_broadcast_media_preview_unauthenticated():
    """Unauthenticated users are redirected to login when accessing media."""
    request = MagicMock(spec=Request)
    bc_id = uuid4()

    with patch("khatmsaz.web.app._admin", new=AsyncMock(return_value=(None, ""))), \
         patch("khatmsaz.web.app._creator", new=AsyncMock(return_value=(None, "", "fa"))):

        res = await broadcast_media_preview(request, bc_id)
        assert res.status_code == 303
        assert "/login" in res.headers["location"]


@pytest.mark.asyncio
async def test_broadcast_media_preview_cached_file(tmp_path):
    """When disk cache exists for media, returns image/jpeg directly."""
    request = MagicMock(spec=Request)
    bc_id = uuid4()
    admin_user = SimpleNamespace(id=uuid4())

    cache_dir = tmp_path / "static" / "uploads" / "broadcasts"
    cache_dir.mkdir(parents=True)
    img_file = cache_dir / f"{bc_id}.jpg"
    img_file.write_bytes(b"\xff\xd8\xff\xe0FAKE_JPEG_CONTENT")

    with patch("khatmsaz.web.app._admin", new=AsyncMock(return_value=(admin_user, "raw"))), \
         patch("khatmsaz.web.app._creator", new=AsyncMock(return_value=(None, "", "fa"))), \
         patch("khatmsaz.web.app.ROOT", tmp_path):

        res = await broadcast_media_preview(request, bc_id)
        assert isinstance(res, Response)
        assert res.media_type == "image/jpeg"
        assert res.body == b"\xff\xd8\xff\xe0FAKE_JPEG_CONTENT"


# --- 5. Template Validations ---

def test_templates_broadcast_media_and_copy():
    """Verify templates contain media image preview and updated copy without PRO plan restriction."""
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent

    # Check broadcasts.html
    bc_tpl = (base_dir / "src" / "khatmsaz" / "web" / "templates" / "broadcasts.html").read_text(encoding="utf-8")
    assert '<img src="/broadcasts/{{ row.item.id }}/media"' in bc_tpl
    assert "row.item.media_type == 'photo'" in bc_tpl

    # Check creator_broadcasts.html
    creator_tpl = (base_dir / "src" / "khatmsaz" / "web" / "templates" / "creator_broadcasts.html").read_text(encoding="utf-8")
    assert "error == 'insufficient_funds'" in creator_tpl
    assert "ویژهٔ پلن حرفه‌ای" not in creator_tpl
