"""Wallet module: toman balance + advertising credit, append-only ledger, and
pending payment intents (ZarinPal IDOR/replay guard)."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from khatmsaz.core.db import Base


class TxType(str, enum.Enum):
    CHARGE = "CHARGE"
    SPEND = "SPEND"
    REFUND = "REFUND"
    CREDIT = "CREDIT"


class InvoiceKind(str, enum.Enum):
    TOPUP = "TOPUP"
    KHATM_CREATION = "KHATM_CREATION"
    PURCHASE = "PURCHASE"


class InvoiceStatus(str, enum.Enum):
    PAID = "PAID"
    REFUNDED = "REFUNDED"


class CouponDiscountType(str, enum.Enum):
    PERCENT = "PERCENT"
    FIXED = "FIXED"


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    balance_toman: Mapped[int] = mapped_column(Integer, default=0)
    credit_toman: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    wallet_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("wallets.id"))
    amount: Mapped[int] = mapped_column(Integer)
    type: Mapped[TxType] = mapped_column()
    ref: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_wallet_transactions_wallet_id", "wallet_id"),)


class WalletInvoice(Base):
    """Immutable purchase amounts plus a small paid/refunded lifecycle."""

    __tablename__ = "wallet_invoices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    kind: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default=InvoiceStatus.PAID.value)
    gross_amount_toman: Mapped[int] = mapped_column(Integer)
    discount_amount_toman: Mapped[int] = mapped_column(Integer, default=0)
    net_amount_toman: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(500))
    external_ref: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    resource_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_wallet_invoices_user_issued", "user_id", "issued_at"),
        Index("ix_wallet_invoices_kind_resource", "kind", "resource_ref"),
    )


class DiscountCoupon(Base):
    __tablename__ = "discount_coupons"

    code: Mapped[str] = mapped_column(String(40), primary_key=True)
    discount_type: Mapped[str] = mapped_column(String(16))
    value: Mapped[int] = mapped_column(Integer)
    min_purchase_toman: Mapped[int] = mapped_column(Integer, default=0)
    max_discount_toman: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_redemption_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    per_user_limit: Mapped[int] = mapped_column(Integer, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CouponRedemption(Base):
    __tablename__ = "coupon_redemptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    coupon_code: Mapped[str] = mapped_column(String(40), ForeignKey("discount_coupons.code"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallet_invoices.id"), unique=True
    )
    discount_amount_toman: Mapped[int] = mapped_column(Integer)
    redeemed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_coupon_redemptions_coupon", "coupon_code"),
        Index("ix_coupon_redemptions_user_coupon", "user_id", "coupon_code"),
    )


class PendingPayment(Base):
    """A payment intent created before redirecting to a payment gateway.

    Prevents IDOR (authority cannot be used to credit another user's wallet)
    and replay (`used=True` after first successful verify, set via an atomic
    compare-and-swap UPDATE — never a read-then-write).
    """

    __tablename__ = "pending_payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    authority: Mapped[str] = mapped_column(String, unique=True)
    amount_toman: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_pending_payments_authority", "authority"),)
