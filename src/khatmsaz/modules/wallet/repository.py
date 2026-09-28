"""Persistence access for wallet — the only place that runs SQL for this module."""

from datetime import datetime

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.wallet.models import (
    InvoiceKind,
    InvoiceStatus,
    CouponRedemption,
    DiscountCoupon,
    PendingPayment,
    TxType,
    Wallet,
    WalletInvoice,
    WalletTransaction,
)


async def get_by_user(session: AsyncSession, user_id) -> Wallet | None:
    stmt = select(Wallet).where(Wallet.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_for_user(session: AsyncSession, user_id) -> Wallet:
    wallet = Wallet(id=new_id(), user_id=user_id)
    session.add(wallet)
    await session.flush()
    return wallet


async def add_balance(session: AsyncSession, wallet_id, amount: int) -> None:
    wallet = await session.get(Wallet, wallet_id)
    if wallet is None:
        return
    wallet.balance_toman += amount
    await session.flush()


async def add_credit(session: AsyncSession, wallet_id, amount: int) -> None:
    wallet = await session.get(Wallet, wallet_id)
    if wallet is None:
        return
    wallet.credit_toman += amount
    await session.flush()


async def record_transaction(
    session: AsyncSession, wallet_id, amount: int, tx_type: TxType, description: str | None = None, ref: str | None = None
) -> WalletTransaction:
    tx = WalletTransaction(id=new_id(), wallet_id=wallet_id, amount=amount, type=tx_type, description=description, ref=ref)
    session.add(tx)
    await session.flush()
    return tx


async def create_paid_invoice(
    session: AsyncSession,
    *,
    user_id,
    kind: InvoiceKind | str,
    gross_amount_toman: int,
    discount_amount_toman: int,
    description: str,
    external_ref: str | None = None,
    resource_ref: str | None = None,
) -> WalletInvoice:
    kind_value = kind.value if isinstance(kind, InvoiceKind) else kind
    invoice = WalletInvoice(
        id=new_id(),
        user_id=user_id,
        kind=kind_value,
        status=InvoiceStatus.PAID.value,
        gross_amount_toman=gross_amount_toman,
        discount_amount_toman=discount_amount_toman,
        net_amount_toman=gross_amount_toman - discount_amount_toman,
        description=description,
        external_ref=external_ref,
        resource_ref=resource_ref,
    )
    session.add(invoice)
    await session.flush()
    return invoice


async def bind_invoice_resource(
    session: AsyncSession, invoice_id, resource_ref: str
) -> WalletInvoice | None:
    invoice = await session.get(WalletInvoice, invoice_id)
    if invoice is None:
        return None
    invoice.resource_ref = resource_ref
    await session.flush()
    return invoice


async def get_paid_invoice_by_resource(
    session: AsyncSession, *, user_id, kind: InvoiceKind | str, resource_ref: str
) -> WalletInvoice | None:
    kind_value = kind.value if isinstance(kind, InvoiceKind) else kind
    result = await session.execute(
        select(WalletInvoice).where(
            WalletInvoice.user_id == user_id,
            WalletInvoice.kind == kind_value,
            WalletInvoice.resource_ref == resource_ref,
            WalletInvoice.status == InvoiceStatus.PAID.value,
        )
    )
    return result.scalar_one_or_none()


async def mark_invoice_refunded(
    session: AsyncSession, invoice_id, refunded_at: datetime
) -> WalletInvoice | None:
    result = await session.execute(
        update(WalletInvoice)
        .where(
            WalletInvoice.id == invoice_id,
            WalletInvoice.status == InvoiceStatus.PAID.value,
        )
        .values(status=InvoiceStatus.REFUNDED.value, refunded_at=refunded_at)
        .returning(WalletInvoice)
    )
    return result.scalar_one_or_none()


async def list_invoices_for_user(
    session: AsyncSession, user_id, *, limit: int = 10
) -> list[WalletInvoice]:
    result = await session.execute(
        select(WalletInvoice)
        .where(WalletInvoice.user_id == user_id)
        .order_by(WalletInvoice.issued_at.desc())
        .limit(max(1, min(limit, 50)))
    )
    return list(result.scalars())


async def get_coupon(
    session: AsyncSession, code: str, *, for_update: bool = False
) -> DiscountCoupon | None:
    stmt = select(DiscountCoupon).where(DiscountCoupon.code == code)
    if for_update:
        stmt = stmt.with_for_update()
    return (await session.execute(stmt)).scalar_one_or_none()


async def upsert_coupon(
    session: AsyncSession,
    *,
    code: str,
    discount_type: str,
    value: int,
    min_purchase_toman: int,
    max_discount_toman: int | None,
    total_redemption_limit: int | None,
    per_user_limit: int,
    created_by_user_id=None,
) -> DiscountCoupon:
    coupon = await session.get(DiscountCoupon, code)
    if coupon is None:
        coupon = DiscountCoupon(code=code, discount_type=discount_type, value=value)
        session.add(coupon)
    coupon.discount_type = discount_type
    coupon.value = value
    coupon.min_purchase_toman = min_purchase_toman
    coupon.max_discount_toman = max_discount_toman
    coupon.total_redemption_limit = total_redemption_limit
    coupon.per_user_limit = per_user_limit
    coupon.enabled = True
    coupon.created_by_user_id = created_by_user_id
    await session.flush()
    return coupon


async def set_coupon_enabled(
    session: AsyncSession, code: str, enabled: bool
) -> DiscountCoupon | None:
    coupon = await session.get(DiscountCoupon, code)
    if coupon is None:
        return None
    coupon.enabled = enabled
    await session.flush()
    return coupon


async def count_coupon_redemptions(
    session: AsyncSession, code: str, *, user_id=None
) -> int:
    stmt = select(func.count()).select_from(CouponRedemption).where(
        CouponRedemption.coupon_code == code
    )
    if user_id is not None:
        stmt = stmt.where(CouponRedemption.user_id == user_id)
    return int((await session.scalar(stmt)) or 0)


async def create_coupon_redemption(
    session: AsyncSession,
    *,
    coupon_code: str,
    user_id,
    invoice_id,
    discount_amount_toman: int,
) -> CouponRedemption:
    redemption = CouponRedemption(
        id=new_id(),
        coupon_code=coupon_code,
        user_id=user_id,
        invoice_id=invoice_id,
        discount_amount_toman=discount_amount_toman,
    )
    session.add(redemption)
    await session.flush()
    return redemption


async def list_coupons(session: AsyncSession, *, limit: int = 50) -> list[DiscountCoupon]:
    result = await session.execute(
        select(DiscountCoupon).order_by(DiscountCoupon.created_at.desc()).limit(limit)
    )
    return list(result.scalars())


async def create_pending_payment(
    session: AsyncSession, *, payment_id, user_id, authority: str, amount_toman: int,
    description: str, expires_at: datetime
) -> PendingPayment:
    payment = PendingPayment(
        id=payment_id, user_id=user_id, authority=authority,
        amount_toman=amount_toman, description=description,
        expires_at=expires_at, used=False,
    )
    session.add(payment)
    await session.flush()
    return payment


async def get_pending_payment_by_id(session: AsyncSession, payment_id) -> PendingPayment | None:
    return await session.get(PendingPayment, payment_id)


async def claim_pending_payment(
    session: AsyncSession, *, authority: str, user_id, now: datetime
) -> PendingPayment | None:
    """Atomically consume a valid intent, preventing IDOR and replay."""
    result = await session.execute(
        update(PendingPayment)
        .where(
            and_(
                PendingPayment.authority == authority,
                PendingPayment.user_id == user_id,
                PendingPayment.used.is_(False),
                PendingPayment.expires_at > now,
            )
        )
        .values(used=True)
        .returning(PendingPayment)
    )
    return result.scalar_one_or_none()


async def delete_expired_unused_payments(session: AsyncSession, *, now: datetime) -> int:
    """Remove dead intents while retaining consumed rows as payment evidence."""
    result = await session.execute(
        delete(PendingPayment).where(
            PendingPayment.used.is_(False),
            PendingPayment.expires_at <= now,
        )
    )
    return int(result.rowcount or 0)
