"""Wallet business logic.

Two balances, never mixed (DOMAIN_MODEL.md §7): `balance_toman` is real
money (refundable to the wallet only, never to a bank); `credit_toman` is
earned (e.g. the advertising-consent program — not built yet) and is spent
first automatically, before touching real money. Every mutation is paired
with an append-only `WalletTransaction` row — nothing is ever just updated
silently.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.wallet import repository
from khatmsaz.modules.wallet.gateway import PaymentGateway, PaymentVerification
from khatmsaz.modules.wallet.models import (
    CouponDiscountType,
    DiscountCoupon,
    InvoiceKind,
    TxType,
    Wallet,
    WalletInvoice,
)
from khatmsaz.core.ids import new_id


class InsufficientFundsError(Exception):
    pass


class InvalidPaymentError(Exception):
    """The callback is not a valid, owned, unexpired, single-use payment."""


class PaymentAlreadyProcessedError(InvalidPaymentError):
    """The PSP callback belongs to a payment already credited once."""


class InvalidCouponError(Exception):
    """A coupon is missing, inactive, out of range, or over its limit."""


async def get_or_create_wallet(session: AsyncSession, user_id) -> Wallet:
    wallet = await repository.get_by_user(session, user_id)
    if wallet is not None:
        return wallet
    return await repository.create_for_user(session, user_id)


async def get_balances(session: AsyncSession, user_id) -> tuple[int, int]:
    """Returns (balance_toman, credit_toman)."""
    wallet = await get_or_create_wallet(session, user_id)
    return wallet.balance_toman, wallet.credit_toman


async def add_cash(
    session: AsyncSession, user_id, amount: int, *, description: str,
    ref: str | None = None
) -> WalletInvoice:
    """Real money added — a completed top-up or a refund. `ref` is the
    payment gateway's transaction reference, when there is one."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    wallet = await get_or_create_wallet(session, user_id)
    await repository.add_balance(session, wallet.id, amount)
    await repository.record_transaction(session, wallet.id, amount, TxType.CHARGE, description, ref)
    return await repository.create_paid_invoice(
        session,
        user_id=user_id,
        kind=InvoiceKind.TOPUP,
        gross_amount_toman=amount,
        discount_amount_toman=0,
        description=description,
        external_ref=ref,
    )


async def grant_reward_credit(session: AsyncSession, user_id, amount: int, *, description: str) -> None:
    """Non-cash credit (e.g. the advertising-consent program, an admin
    goodwill grant). Never refundable to a bank — DOMAIN_MODEL.md §7."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    wallet = await get_or_create_wallet(session, user_id)
    await repository.add_credit(session, wallet.id, amount)
    await repository.record_transaction(session, wallet.id, amount, TxType.CREDIT, description)


async def spend(
    session: AsyncSession,
    user_id,
    amount: int,
    *,
    description: str,
    invoice_kind: InvoiceKind = InvoiceKind.PURCHASE,
    gross_amount_toman: int | None = None,
    discount_amount_toman: int = 0,
) -> WalletInvoice:
    """Spend `amount`, taking from `credit_toman` first, then
    `balance_toman`. Raises InsufficientFundsError (no partial spend) if the
    combined total isn't enough — checked before any mutation happens."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    gross = amount if gross_amount_toman is None else gross_amount_toman
    if gross <= 0 or discount_amount_toman < 0 or gross - discount_amount_toman != amount:
        raise ValueError("invoice amounts do not reconcile")

    wallet = await get_or_create_wallet(session, user_id)
    total_available = wallet.balance_toman + wallet.credit_toman
    if total_available < amount:
        raise InsufficientFundsError(
            f"need {amount}, have {total_available} (balance={wallet.balance_toman}, credit={wallet.credit_toman})"
        )

    from_credit = min(wallet.credit_toman, amount)
    from_balance = amount - from_credit

    if from_credit > 0:
        await repository.add_credit(session, wallet.id, -from_credit)
        await repository.record_transaction(session, wallet.id, -from_credit, TxType.SPEND, f"{description} (credit)")
    if from_balance > 0:
        await repository.add_balance(session, wallet.id, -from_balance)
        await repository.record_transaction(session, wallet.id, -from_balance, TxType.SPEND, f"{description} (balance)")
    return await repository.create_paid_invoice(
        session,
        user_id=user_id,
        kind=invoice_kind,
        gross_amount_toman=gross,
        discount_amount_toman=discount_amount_toman,
        description=description,
    )


def _coupon_discount(coupon: DiscountCoupon, gross_amount_toman: int) -> int:
    if coupon.discount_type == CouponDiscountType.PERCENT.value:
        discount = gross_amount_toman * coupon.value // 100
        if coupon.max_discount_toman is not None:
            discount = min(discount, coupon.max_discount_toman)
    else:
        discount = coupon.value
    return min(gross_amount_toman, max(0, discount))


async def _validate_coupon(
    session: AsyncSession,
    *,
    code: str,
    user_id,
    gross_amount_toman: int,
    for_update: bool,
) -> tuple[DiscountCoupon, int]:
    normalized = code.strip().upper()
    coupon = await repository.get_coupon(session, normalized, for_update=for_update)
    now = datetime.now(timezone.utc)
    if coupon is None or not coupon.enabled:
        raise InvalidCouponError("coupon is missing or disabled")
    if coupon.starts_at is not None and coupon.starts_at > now:
        raise InvalidCouponError("coupon has not started")
    if coupon.ends_at is not None and coupon.ends_at <= now:
        raise InvalidCouponError("coupon has expired")
    if gross_amount_toman < coupon.min_purchase_toman:
        raise InvalidCouponError("purchase is below coupon minimum")
    total_used = await repository.count_coupon_redemptions(session, normalized)
    if coupon.total_redemption_limit is not None and total_used >= coupon.total_redemption_limit:
        raise InvalidCouponError("coupon redemption limit reached")
    user_used = await repository.count_coupon_redemptions(
        session, normalized, user_id=user_id
    )
    if user_used >= coupon.per_user_limit:
        raise InvalidCouponError("user redemption limit reached")
    discount = _coupon_discount(coupon, gross_amount_toman)
    if discount <= 0:
        raise InvalidCouponError("coupon has no usable discount")
    return coupon, discount


async def quote_coupon(
    session: AsyncSession, *, code: str, user_id, gross_amount_toman: int
) -> int:
    _, discount = await _validate_coupon(
        session,
        code=code,
        user_id=user_id,
        gross_amount_toman=gross_amount_toman,
        for_update=False,
    )
    return discount


async def purchase(
    session: AsyncSession,
    *,
    user_id,
    gross_amount_toman: int,
    description: str,
    invoice_kind: InvoiceKind,
    coupon_code: str | None = None,
) -> WalletInvoice:
    if gross_amount_toman <= 0:
        raise ValueError("gross amount must be positive")
    coupon = None
    discount = 0
    if coupon_code:
        coupon, discount = await _validate_coupon(
            session,
            code=coupon_code,
            user_id=user_id,
            gross_amount_toman=gross_amount_toman,
            for_update=True,
        )
    net = gross_amount_toman - discount
    if net > 0:
        invoice = await spend(
            session,
            user_id,
            net,
            description=description,
            invoice_kind=invoice_kind,
            gross_amount_toman=gross_amount_toman,
            discount_amount_toman=discount,
        )
    else:
        invoice = await repository.create_paid_invoice(
            session,
            user_id=user_id,
            kind=invoice_kind,
            gross_amount_toman=gross_amount_toman,
            discount_amount_toman=discount,
            description=description,
        )
    if coupon is not None:
        await repository.create_coupon_redemption(
            session,
            coupon_code=coupon.code,
            user_id=user_id,
            invoice_id=invoice.id,
            discount_amount_toman=discount,
        )
    return invoice


async def set_coupon(
    session: AsyncSession,
    *,
    code: str,
    discount_type: CouponDiscountType,
    value: int,
    min_purchase_toman: int = 0,
    max_discount_toman: int | None = None,
    total_redemption_limit: int | None = None,
    per_user_limit: int = 1,
    created_by_user_id=None,
):
    normalized = code.strip().upper()
    if not (3 <= len(normalized) <= 40) or not all(
        char.isascii() and (char.isalnum() or char in "_-") for char in normalized
    ):
        raise ValueError("coupon code must be 3-40 ASCII letters, digits, _ or -")
    if value <= 0 or min_purchase_toman < 0 or per_user_limit <= 0:
        raise ValueError("coupon values must be positive")
    if discount_type == CouponDiscountType.PERCENT and value > 100:
        raise ValueError("percent discount cannot exceed 100")
    if max_discount_toman is not None and max_discount_toman <= 0:
        raise ValueError("max discount must be positive")
    if total_redemption_limit is not None and total_redemption_limit <= 0:
        raise ValueError("total limit must be positive")
    return await repository.upsert_coupon(
        session,
        code=normalized,
        discount_type=discount_type.value,
        value=value,
        min_purchase_toman=min_purchase_toman,
        max_discount_toman=max_discount_toman,
        total_redemption_limit=total_redemption_limit,
        per_user_limit=per_user_limit,
        created_by_user_id=created_by_user_id,
    )


async def set_coupon_enabled(session: AsyncSession, code: str, enabled: bool):
    return await repository.set_coupon_enabled(session, code.strip().upper(), enabled)


async def list_coupons(session: AsyncSession):
    return await repository.list_coupons(session)


async def refund_cash(session: AsyncSession, user_id, amount: int, *, description: str) -> None:
    """Refund to the wallet's real-money balance — never to a bank account
    (DOMAIN_MODEL.md §7's "refund before first join" rule uses this)."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    wallet = await get_or_create_wallet(session, user_id)
    await repository.add_balance(session, wallet.id, amount)
    await repository.record_transaction(session, wallet.id, amount, TxType.REFUND, description)


async def bind_invoice_resource(
    session: AsyncSession, invoice_id, resource_ref: str
) -> WalletInvoice:
    invoice = await repository.bind_invoice_resource(session, invoice_id, resource_ref)
    if invoice is None:
        raise ValueError("invoice was not found")
    return invoice


async def refund_purchase_invoice(
    session: AsyncSession,
    *,
    user_id,
    kind: InvoiceKind,
    resource_ref: str,
    description: str,
) -> int | None:
    """Refund a paid purchase once; return None when no invoice exists."""
    invoice = await repository.get_paid_invoice_by_resource(
        session, user_id=user_id, kind=kind, resource_ref=resource_ref
    )
    if invoice is None:
        return None
    marked = await repository.mark_invoice_refunded(
        session, invoice.id, datetime.now(timezone.utc)
    )
    if marked is None:
        raise InvalidPaymentError("invoice was already refunded")
    await refund_cash(
        session, user_id, invoice.net_amount_toman, description=description
    )
    return invoice.net_amount_toman


async def list_invoices(session: AsyncSession, user_id, *, limit: int = 10):
    return await repository.list_invoices_for_user(session, user_id, limit=limit)


async def create_payment_intent(
    session: AsyncSession,
    gateway: PaymentGateway,
    user_id,
    *,
    amount_toman: int,
    description: str,
    callback_url: str,
    expires_in_minutes: int = 30,
):
    """Ask a PSP for an authority, then bind it to this exact user/amount."""
    if amount_toman <= 0 or expires_in_minutes <= 0:
        raise ValueError("amount and expiry must be positive")
    payment_id = new_id()
    request = await gateway.request_payment(
        amount_toman=amount_toman,
        description=description,
        callback_url=callback_url,
        client_ref_id=str(payment_id),
    )
    return await repository.create_pending_payment(
        session,
        payment_id=payment_id,
        user_id=user_id,
        authority=request.authority,
        amount_toman=amount_toman,
        description=description,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes),
    ), request


async def verify_and_credit(
    session: AsyncSession,
    gateway: PaymentGateway,
    user_id,
    *,
    authority: str,
    transaction_ref: str = "",
    now: datetime | None = None,
) -> PaymentVerification:
    """Verify with the PSP and atomically consume the matching intent.

    The intent is claimed only after the gateway confirms it. The CAS also
    checks the callback's user ownership and expiry, so replay and IDOR do not
    credit another wallet. A failed wallet mutation rolls back the claim.
    """
    current = now or datetime.now(timezone.utc)
    from sqlalchemy import select
    from khatmsaz.modules.wallet.models import PendingPayment

    pending_result = await session.execute(
        select(PendingPayment).where(PendingPayment.authority == authority)
    )
    pending = pending_result.scalar_one_or_none()
    if pending is None or pending.user_id != user_id or pending.used or pending.expires_at <= current:
        raise InvalidPaymentError("payment intent is invalid, expired, used, or owned by another user")

    verification = await gateway.verify_payment(
        authority=authority,
        amount_toman=pending.amount_toman,
        transaction_ref=transaction_ref,
        client_ref_id=str(pending.id),
    )
    if (
        verification.authority != authority
        or verification.amount_toman != pending.amount_toman
        or not verification.transaction_ref
    ):
        raise InvalidPaymentError("gateway verification does not match the payment intent")

    claimed = await repository.claim_pending_payment(
        session, authority=authority, user_id=user_id, now=current
    )
    if claimed is None:
        raise InvalidPaymentError("payment intent was already consumed or expired")
    await add_cash(
        session, user_id, claimed.amount_toman,
        description=claimed.description, ref=verification.transaction_ref,
    )
    return verification


async def verify_payping_callback_and_credit(
    session: AsyncSession,
    gateway: PaymentGateway,
    *,
    client_ref_id: str,
    authority: str,
    amount_toman: int,
    transaction_ref: str,
    now: datetime | None = None,
) -> PaymentVerification:
    """Validate PayPing's untrusted form callback, verify it, then credit once.

    ``client_ref_id`` is the UUID generated locally before the PSP request.
    It is never accepted as a user id: the wallet owner comes only from the
    stored pending-payment row.  The callback's payment code and amount must
    also match that row before the PSP verification call is made.
    """
    try:
        payment_id = UUID(client_ref_id)
    except (TypeError, ValueError) as exc:
        raise InvalidPaymentError("invalid client reference") from exc

    current = now or datetime.now(timezone.utc)
    pending = await repository.get_pending_payment_by_id(session, payment_id)
    if pending is None:
        raise InvalidPaymentError("payment intent was not found")
    if pending.authority != authority or pending.amount_toman != amount_toman:
        raise InvalidPaymentError("callback does not match the stored payment intent")
    if pending.used:
        raise PaymentAlreadyProcessedError("payment was already credited")
    if pending.expires_at <= current or not transaction_ref:
        raise InvalidPaymentError("payment intent expired or has no transaction reference")

    verification = await gateway.verify_payment(
        authority=authority,
        amount_toman=pending.amount_toman,
        transaction_ref=transaction_ref,
        client_ref_id=str(pending.id),
    )
    if (
        verification.authority != authority
        or verification.amount_toman != pending.amount_toman
        or verification.transaction_ref != transaction_ref
    ):
        raise InvalidPaymentError("gateway verification does not match the payment intent")

    claimed = await repository.claim_pending_payment(
        session, authority=authority, user_id=pending.user_id, now=current
    )
    if claimed is None:
        raise PaymentAlreadyProcessedError("payment was already credited or expired")
    await add_cash(
        session,
        pending.user_id,
        claimed.amount_toman,
        description=claimed.description,
        ref=verification.transaction_ref,
    )
    return verification
