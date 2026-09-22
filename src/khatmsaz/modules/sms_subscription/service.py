"""SMS subscription business logic (owner request, 2026-09-20): SMS
reminders require a paid, time-limited subscription; expiry must turn SMS
off automatically and notify the user — never silently continue or
silently go quiet."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.sms_subscription import repository
from khatmsaz.modules.sms_subscription.models import SmsPlanOption
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.models import InvoiceKind

_DAYS_PER_MONTH = 30  # Plain calendar approximation, consistent everywhere in this module.


class SmsPlanUnavailableError(Exception):
    """The requested duration isn't a configured, enabled plan option."""


class SmsContactPhoneRequiredError(Exception):
    """A paid SMS plan cannot be charged before a destination exists."""


async def list_options(session: AsyncSession) -> list[SmsPlanOption]:
    return await repository.list_active_options(session)


async def set_option(session: AsyncSession, *, months: int, price_toman: int, enabled: bool) -> SmsPlanOption:
    if months <= 0:
        raise ValueError("months must be positive")
    if price_toman < 0:
        raise ValueError("price cannot be negative")
    return await repository.upsert_option(session, months=months, price_toman=price_toman, enabled=enabled)


async def get_expiry(session: AsyncSession, user_id) -> datetime | None:
    sub = await repository.get_subscription(session, user_id)
    return sub.expires_at if sub is not None else None


async def is_active(session: AsyncSession, user_id, *, now: datetime | None = None) -> bool:
    expires_at = await get_expiry(session, user_id)
    if expires_at is None:
        return False
    current = now or datetime.now(timezone.utc)
    return expires_at > current


async def purchase(session: AsyncSession, user_id, months: int, *, coupon_code: str | None = None) -> datetime:
    """Charge the wallet for one SMS plan option, extend the subscription
    from whichever is later (now, or the current expiry if still active —
    so buying early never wastes remaining paid time), and turn SMS on.
    Returns the new expiry."""
    option = await repository.get_option(session, months)
    if option is None or not option.enabled:
        raise SmsPlanUnavailableError(f"no enabled SMS plan for {months} months")
    # This precondition must run before wallet_service.purchase. Catching a
    # later set_sms_enabled ValueError in the HTTP/bot boundary would otherwise
    # let session_scope commit the debit while returning "add a phone first".
    settings = await settings_service.get_or_create(session, user_id)
    if not settings.contact_phone:
        raise SmsContactPhoneRequiredError("contact phone required before purchase")
    if option.price_toman > 0:
        await wallet_service.purchase(
            session, user_id=user_id, gross_amount_toman=option.price_toman,
            description=f"اشتراک پیامک یادآوری - {months} ماهه",
            invoice_kind=InvoiceKind.PURCHASE, coupon_code=coupon_code,
        )
    now = datetime.now(timezone.utc)
    current_expiry = await get_expiry(session, user_id)
    base = current_expiry if current_expiry and current_expiry > now else now
    new_expiry = base + timedelta(days=_DAYS_PER_MONTH * months)
    await repository.upsert_subscription(session, user_id, new_expiry)
    await settings_service.set_sms_enabled(session, user_id, True)
    return new_expiry


async def process_expired(session: AsyncSession, notify) -> int:
    """Called from the periodic scan (owner request): find subscriptions
    that just lapsed, turn SMS off, and notify the user once per lapse.
    Returns how many were processed."""
    from khatmsaz.modules.identity import service as identity_service

    now = datetime.now(timezone.utc)
    expired = await repository.list_newly_expired(session, now=now)
    for sub in expired:
        try:
            await settings_service.set_sms_enabled(session, sub.user_id, False)
        except ValueError:
            pass  # Already effectively off (no contact phone) — nothing to disable.
        identities = await identity_service.list_identities_for_user(session, sub.user_id)
        for identity in identities:
            await notify(
                identity.platform.value, identity.subject,
                "⏳ اشتراک پیامک یادآوریِ شما تمام شد و پیامک‌ها خاموش شدند. "
                "برای فعال‌سازی دوباره، از منوی ⚙️ تنظیمات یک اشتراک تازه بخرید.",
            )
        await repository.mark_notified(session, sub)
    return len(expired)
