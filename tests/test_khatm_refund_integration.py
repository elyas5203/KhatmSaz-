import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm_workflow import service as workflow_service
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.wallet.models import InvoiceKind, InvoiceStatus, Wallet, WalletInvoice, WalletTransaction
from khatmsaz.modules.wallet import repository as wallet_repository


@pytest.mark.integration
@pytest.mark.asyncio
async def test_unused_paid_khatm_cancels_and_refunds_cash_balance():
    user_id, khatm_id = new_id(), new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        await session.flush()
        session.add(Khatm(
            id=khatm_id, creator_user_id=user_id, title="بازپرداخت آزمایشی",
            template_type=KhatmTemplateType.SALAWAT, khatm_type=KhatmTypeEnum.OPEN,
            status=KhatmStatus.ACTIVE, creation_price_toman=2500,
        ))
        await session.flush()
        invoice = await wallet_repository.create_paid_invoice(
            session,
            user_id=user_id,
            kind=InvoiceKind.KHATM_CREATION,
            gross_amount_toman=2500,
            discount_amount_toman=0,
            description="ساخت ختم آزمایشی",
            resource_ref=str(khatm_id),
        )

        khatm, refunded = await workflow_service.cancel_khatm(
            session, khatm_id=khatm_id, creator_user_id=user_id
        )
        assert khatm.status == KhatmStatus.CANCELLED
        assert refunded == 2500
        wallet = await wallet_repository.get_by_user(session, user_id)
        assert wallet is not None
        assert wallet.balance_toman == 2500
        await session.refresh(invoice)
        assert invoice.status == InvoiceStatus.REFUNDED.value
        assert invoice.refunded_at is not None

        await session.execute(delete(WalletTransaction).where(WalletTransaction.wallet_id == wallet.id))
        await session.execute(delete(WalletInvoice).where(WalletInvoice.user_id == user_id))
        await session.execute(delete(Wallet).where(Wallet.id == wallet.id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id == user_id))
