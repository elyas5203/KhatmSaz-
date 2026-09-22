"""Real PostgreSQL coverage for bounded, auditable coupon redemption."""

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.wallet import service
from khatmsaz.modules.wallet.models import (
    CouponDiscountType,
    CouponRedemption,
    DiscountCoupon,
    InvoiceKind,
    Wallet,
    WalletInvoice,
    WalletTransaction,
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_coupon_discount_invoice_and_limits_are_atomic():
    first_id, second_id = new_id(), new_id()
    async with session_scope() as session:
        session.add_all([User(id=first_id), User(id=second_id)])
        await session.flush()
        first_wallet = await service.get_or_create_wallet(session, first_id)
        second_wallet = await service.get_or_create_wallet(session, second_id)
        first_wallet.balance_toman = 10_000
        second_wallet.balance_toman = 10_000
        await service.set_coupon(
            session,
            code="khatm20",
            discount_type=CouponDiscountType.PERCENT,
            value=20,
            min_purchase_toman=5_000,
            max_discount_toman=3_000,
            total_redemption_limit=1,
            per_user_limit=1,
        )

        assert await service.quote_coupon(
            session, code="KHATM20", user_id=first_id, gross_amount_toman=10_000
        ) == 2_000
        invoice = await service.purchase(
            session,
            user_id=first_id,
            gross_amount_toman=10_000,
            description="خرید آزمایشی",
            invoice_kind=InvoiceKind.PURCHASE,
            coupon_code="khatm20",
        )
        assert invoice.gross_amount_toman == 10_000
        assert invoice.discount_amount_toman == 2_000
        assert invoice.net_amount_toman == 8_000
        assert first_wallet.balance_toman == 2_000

        with pytest.raises(service.InvalidCouponError):
            await service.purchase(
                session,
                user_id=second_id,
                gross_amount_toman=10_000,
                description="نباید ثبت شود",
                invoice_kind=InvoiceKind.PURCHASE,
                coupon_code="KHATM20",
            )
        assert second_wallet.balance_toman == 10_000

        await session.execute(delete(CouponRedemption).where(CouponRedemption.coupon_code == "KHATM20"))
        await session.execute(delete(WalletTransaction).where(WalletTransaction.wallet_id.in_([first_wallet.id, second_wallet.id])))
        await session.execute(delete(WalletInvoice).where(WalletInvoice.user_id.in_([first_id, second_id])))
        await session.execute(delete(DiscountCoupon).where(DiscountCoupon.code == "KHATM20"))
        await session.execute(delete(Wallet).where(Wallet.id.in_([first_wallet.id, second_wallet.id])))
        await session.execute(delete(User).where(User.id.in_([first_id, second_id])))
