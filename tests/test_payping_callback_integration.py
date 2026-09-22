"""PostgreSQL + ASGI coverage for the public PayPing callback."""

import json

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.wallet import repository, service
from khatmsaz.modules.wallet.gateway import PaymentRequest, PaymentVerification
from khatmsaz.modules.wallet.models import PendingPayment, Wallet, WalletInvoice, WalletTransaction
import khatmsaz.web.app as web_app_module


class CallbackGateway:
    async def request_payment(
        self, *, amount_toman, description, callback_url, client_ref_id
    ):
        return PaymentRequest(
            authority="payping-callback-integration",
            payment_url="https://example.invalid/pay",
        )

    async def verify_payment(
        self, *, authority, amount_toman, transaction_ref, client_ref_id
    ):
        return PaymentVerification(
            authority=authority,
            amount_toman=amount_toman,
            transaction_ref=transaction_ref,
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_payping_callback_credits_once_and_replay_is_idempotent(monkeypatch):
    gateway = CallbackGateway()
    user_id = new_id()
    async with session_scope() as session:
        session.add(User(id=user_id))
        await session.flush()
        pending, _ = await service.create_payment_intent(
            session,
            gateway,
            user_id,
            amount_toman=50_000,
            description="شارژ تست پی‌پینگ",
            callback_url="https://khatmsaz.com/payments/payping/callback",
        )

    monkeypatch.setattr(web_app_module, "_payment_gateway", lambda: gateway)
    callback_data = json.dumps(
        {
            "clientRefId": str(pending.id),
            "paymentCode": pending.authority,
            "paymentRefId": 987654,
            "amount": 50_000,
        }
    )
    transport = ASGITransport(app=web_app_module.app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post(
            "/payments/payping/callback", data={"status": "1", "data": callback_data}
        )
        replay = await client.post(
            "/payments/payping/callback", data={"status": "1", "data": callback_data}
        )
        forged = await client.post(
            "/payments/payping/callback",
            data={
                "status": "1",
                "data": json.dumps(
                    {
                        "clientRefId": str(pending.id),
                        "paymentCode": pending.authority,
                        "paymentRefId": 987654,
                        "amount": 500_000,
                    }
                ),
            },
        )

    assert first.status_code == 200
    assert "کیف پول شارژ شد" in first.text
    assert replay.status_code == 200
    assert "قبلاً ثبت شده" in replay.text
    assert forged.status_code == 400

    async with session_scope() as session:
        wallet = await repository.get_by_user(session, user_id)
        assert wallet is not None
        assert wallet.balance_toman == 50_000
        tx_count = len(
            list(
                (
                    await session.execute(
                        __import__("sqlalchemy").select(WalletTransaction).where(
                            WalletTransaction.wallet_id == wallet.id
                        )
                    )
                ).scalars()
            )
        )
        assert tx_count == 1
        invoices = await service.list_invoices(session, user_id)
        assert len(invoices) == 1
        assert invoices[0].kind == "TOPUP"
        assert invoices[0].external_ref == "987654"
        await session.execute(
            delete(WalletTransaction).where(WalletTransaction.wallet_id == wallet.id)
        )
        await session.execute(delete(WalletInvoice).where(WalletInvoice.user_id == user_id))
        await session.execute(delete(PendingPayment).where(PendingPayment.id == pending.id))
        await session.execute(delete(Wallet).where(Wallet.id == wallet.id))
        await session.execute(delete(User).where(User.id == user_id))
