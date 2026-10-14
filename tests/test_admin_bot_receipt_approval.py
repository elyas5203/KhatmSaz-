import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from aiogram.types import CallbackQuery, Message, User as TgUser

from khatmsaz.bot.handlers.admin_bot.handlers import approve_receipt_admin_bot, reject_receipt_admin_bot
from khatmsaz.modules.identity.models import Platform, User, UserRole
from khatmsaz.modules.wallet.models import ReceiptClaimStatus, WalletReceiptClaim


@pytest.mark.asyncio
async def test_admin_bot_approves_receipt_successfully():
    claim_id = uuid4()
    user_id = uuid4()
    admin_uid = uuid4()

    mock_claim = MagicMock(spec=WalletReceiptClaim)
    mock_claim.id = claim_id
    mock_claim.user_id = user_id
    mock_claim.amount_toman = 10_000
    mock_claim.status = ReceiptClaimStatus.PENDING.value

    mock_admin_user = User(id=admin_uid, role=UserRole.SUPER_ADMIN, display_name="مدیر کل")

    cb = AsyncMock(spec=CallbackQuery)
    cb.data = f"receipt:approve:{claim_id}"
    cb.from_user = TgUser(id=999999, is_bot=False, first_name="Admin", full_name="Super Admin")
    cb.message = AsyncMock(spec=Message)
    cb.message.caption = "فیش واریزی"
    cb.message.photo = True
    cb.message.edit_caption = AsyncMock()
    cb.answer = AsyncMock()
    cb.bot = AsyncMock()
    cb.bot.khatmsaz_platform = Platform.TELEGRAM

    with patch("khatmsaz.bot.handlers.admin_bot.handlers._is_super_admin", new=AsyncMock(return_value=True)), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.identity_service.resolve_or_provision_user", new=AsyncMock(return_value=mock_admin_user)), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.identity_service.list_identities_for_user", new=AsyncMock(return_value=[])), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.wallet_service.get_receipt_claim", new=AsyncMock(return_value=mock_claim)), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.wallet_service.approve_receipt_claim", new=AsyncMock(return_value=(mock_claim, None))) as mock_approve, \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.wallet_service.get_balances", new=AsyncMock(return_value=(15_000, 0))):

        mock_session = AsyncMock()
        mock_scope.return_value.__aenter__.return_value = mock_session

        await approve_receipt_admin_bot(cb)

        mock_approve.assert_awaited_once_with(
            mock_session,
            claim_id=claim_id,
            admin_user_id=mock_admin_user.id,
        )
        cb.message.edit_caption.assert_awaited_once()
        cb.answer.assert_awaited_once()
        assert "موفقیت" in cb.answer.call_args[0][0] or "تأیید شد" in cb.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_admin_bot_rejects_receipt_successfully():
    claim_id = uuid4()
    user_id = uuid4()
    admin_uid = uuid4()

    mock_claim = MagicMock(spec=WalletReceiptClaim)
    mock_claim.id = claim_id
    mock_claim.user_id = user_id
    mock_claim.amount_toman = 10_000
    mock_claim.status = ReceiptClaimStatus.PENDING.value

    mock_admin_user = User(id=admin_uid, role=UserRole.SUPER_ADMIN, display_name="مدیر کل")

    cb = AsyncMock(spec=CallbackQuery)
    cb.data = f"receipt:reject:{claim_id}"
    cb.from_user = TgUser(id=999999, is_bot=False, first_name="Admin", full_name="Super Admin")
    cb.message = AsyncMock(spec=Message)
    cb.message.caption = "فیش واریزی"
    cb.message.photo = True
    cb.message.edit_caption = AsyncMock()
    cb.answer = AsyncMock()
    cb.bot = AsyncMock()
    cb.bot.khatmsaz_platform = Platform.TELEGRAM

    with patch("khatmsaz.bot.handlers.admin_bot.handlers._is_super_admin", new=AsyncMock(return_value=True)), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.identity_service.resolve_or_provision_user", new=AsyncMock(return_value=mock_admin_user)), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.identity_service.list_identities_for_user", new=AsyncMock(return_value=[])), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.wallet_service.get_receipt_claim", new=AsyncMock(return_value=mock_claim)), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.wallet_service.reject_receipt_claim", new=AsyncMock(return_value=mock_claim)) as mock_reject:

        mock_session = AsyncMock()
        mock_scope.return_value.__aenter__.return_value = mock_session

        await reject_receipt_admin_bot(cb)

        mock_reject.assert_awaited_once_with(
            mock_session,
            claim_id=claim_id,
            admin_user_id=mock_admin_user.id,
        )
        cb.message.edit_caption.assert_awaited_once()
        cb.answer.assert_awaited_once()
        assert "رد شد" in cb.answer.call_args[0][0]
