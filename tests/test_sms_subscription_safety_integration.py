"""Financial safety regression for SMS subscription purchases."""

import pytest
from sqlalchemy import delete, func, select

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.settings.models import UserSettings
from khatmsaz.modules.sms_subscription import service as sms_subscription_service
from khatmsaz.modules.sms_subscription.models import SmsSubscription
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.models import Wallet, WalletInvoice, WalletTransaction


@pytest.mark.integration
@pytest.mark.asyncio
async def test_missing_phone_is_rejected_before_any_sms_plan_debit_or_invoice():
    user_id = new_id()
    async with session_scope() as session:
        session.add(User(id=user_id, display_name="کاربر بدون شماره"))
        await session.flush()
        await settings_service.get_or_create(session, user_id)
        wallet = await wallet_service.get_or_create_wallet(session, user_id)
        wallet.balance_toman = 100_000
        await session.flush()

        with pytest.raises(sms_subscription_service.SmsContactPhoneRequiredError):
            await sms_subscription_service.purchase(session, user_id, 3)

        await session.refresh(wallet)
        assert wallet.balance_toman == 100_000
        assert await session.scalar(
            select(func.count()).select_from(WalletInvoice).where(WalletInvoice.user_id == user_id)
        ) == 0
        assert await session.get(SmsSubscription, user_id) is None

    # Prove the no-charge state survived the session commit, which is the
    # exact boundary where the old handler could commit a partial purchase.
    async with session_scope() as session:
        wallet = await session.scalar(select(Wallet).where(Wallet.user_id == user_id))
        assert wallet.balance_toman == 100_000
        assert await session.scalar(
            select(func.count()).select_from(WalletInvoice).where(WalletInvoice.user_id == user_id)
        ) == 0

        await session.execute(delete(WalletTransaction).where(WalletTransaction.wallet_id == wallet.id))
        await session.execute(delete(WalletInvoice).where(WalletInvoice.user_id == user_id))
        await session.execute(delete(Wallet).where(Wallet.id == wallet.id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
