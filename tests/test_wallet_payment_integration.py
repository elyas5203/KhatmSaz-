"""Real PostgreSQL coverage for payment ownership and replay protection."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.wallet import repository, service
from khatmsaz.modules.wallet.gateway import PaymentRequest, PaymentVerification
from khatmsaz.modules.wallet.models import PendingPayment, Wallet, WalletInvoice, WalletTransaction


class FakeGateway:
    async def request_payment(self, *, amount_toman, description, callback_url, client_ref_id):
        return PaymentRequest(authority="pytest-authority-" + uuid.uuid4().hex, payment_url="https://example.invalid")

    async def verify_payment(self, *, authority, amount_toman, transaction_ref, client_ref_id):
        return PaymentVerification(
            authority=authority,
            amount_toman=amount_toman,
            transaction_ref=transaction_ref or "pytest-ref",
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_payment_intent_is_owned_single_use_and_amount_bound():
    gateway = FakeGateway()
    async with session_scope() as session:
        owner_id = new_id()
        other_id = new_id()
        session.add_all([User(id=owner_id), User(id=other_id)])
        await session.flush()

        payment, _ = await service.create_payment_intent(
            session,
            gateway,
            owner_id,
            amount_toman=12345,
            description="pytest payment",
            callback_url="https://example.invalid/callback",
        )

        with pytest.raises(service.InvalidPaymentError):
            await service.verify_and_credit(session, gateway, other_id, authority=payment.authority)

        verification = await service.verify_and_credit(
            session, gateway, owner_id, authority=payment.authority
        )
        assert verification.transaction_ref == "pytest-ref"
        wallet = await repository.get_by_user(session, owner_id)
        assert wallet is not None
        assert wallet.balance_toman == 12345
        invoices = await service.list_invoices(session, owner_id)
        assert len(invoices) == 1
        assert invoices[0].kind == "TOPUP"
        assert invoices[0].net_amount_toman == 12345

        with pytest.raises(service.InvalidPaymentError):
            await service.verify_and_credit(session, gateway, owner_id, authority=payment.authority)

        # Keep the persistent integration database clean after a successful run.
        await session.execute(delete(WalletTransaction).where(WalletTransaction.wallet_id == wallet.id))
        await session.execute(delete(WalletInvoice).where(WalletInvoice.user_id == owner_id))
        await session.execute(delete(PendingPayment).where(PendingPayment.id == payment.id))
        await session.execute(delete(Wallet).where(Wallet.id == wallet.id))
        await session.execute(delete(User).where(User.id.in_([owner_id, other_id])))
