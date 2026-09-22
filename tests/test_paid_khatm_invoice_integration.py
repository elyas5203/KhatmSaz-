"""A paid khatm has one bound invoice and cancellation refunds that invoice."""

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.invitation.models import KhatmInvitation
from khatmsaz.modules.khatm.models import Khatm, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm_workflow import service as workflow_service
from khatmsaz.modules.wallet import repository as wallet_repository
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.models import InvoiceStatus, Wallet, WalletInvoice, WalletTransaction
from khatmsaz.modules.wallet.models import CouponDiscountType, CouponRedemption, DiscountCoupon


@pytest.mark.integration
@pytest.mark.asyncio
async def test_paid_khatm_invoice_is_bound_and_refunded_once():
    user_id = new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        await session.flush()
        wallet = await wallet_service.get_or_create_wallet(session, user_id)
        wallet.balance_toman = 10_000
        await session.flush()
        await wallet_service.set_coupon(
            session,
            code="CREATE500",
            discount_type=CouponDiscountType.FIXED,
            value=500,
            min_purchase_toman=2_000,
            total_redemption_limit=10,
            per_user_limit=1,
        )

        khatm, _ = await workflow_service.create_and_launch_khatm(
            session,
            creator_user_id=user_id,
            template_type=KhatmTemplateType.SALAWAT,
            khatm_type=KhatmTypeEnum.OPEN,
            title="ختم پولی آزمایشی",
            niyyat=None,
            salawat_open_target=1_000,
            creation_price_toman=2_500,
            coupon_code="CREATE500",
        )
        invoices = await wallet_service.list_invoices(session, user_id)
        assert len(invoices) == 1
        invoice = invoices[0]
        assert invoice.kind == "KHATM_CREATION"
        assert invoice.resource_ref == str(khatm.id)
        assert invoice.gross_amount_toman == 2_500
        assert invoice.discount_amount_toman == 500
        assert invoice.net_amount_toman == 2_000
        assert khatm.creation_price_toman == 2_000
        assert wallet.balance_toman == 8_000

        _, refunded = await workflow_service.cancel_khatm(
            session, khatm_id=khatm.id, creator_user_id=user_id
        )
        assert refunded == 2_000
        assert wallet.balance_toman == 10_000
        await session.refresh(invoice)
        assert invoice.status == InvoiceStatus.REFUNDED.value

        await session.execute(delete(KhatmInvitation).where(KhatmInvitation.khatm_id == khatm.id))
        await session.execute(delete(CouponRedemption).where(CouponRedemption.coupon_code == "CREATE500"))
        await session.execute(delete(WalletTransaction).where(WalletTransaction.wallet_id == wallet.id))
        await session.execute(delete(WalletInvoice).where(WalletInvoice.user_id == user_id))
        await session.execute(delete(DiscountCoupon).where(DiscountCoupon.code == "CREATE500"))
        await session.execute(delete(Wallet).where(Wallet.id == wallet.id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm.id))
        await session.execute(delete(User).where(User.id == user_id))
