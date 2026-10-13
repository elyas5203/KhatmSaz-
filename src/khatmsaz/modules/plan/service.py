import math
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.plan import repository
from khatmsaz.modules.plan.models import PlanTier, PricingMode
from khatmsaz.modules.wallet import service as wallet_service


class PlanFeatureUnavailableError(Exception):
    """The active plan does not permit the requested feature."""


_PRO_PLAN_DURATION_DAYS = 30


async def get_plan(session: AsyncSession, user_id) -> PlanTier:
    """The user's active plan tier — FREE / BASIC / PRO (missing row = FREE).

    Owner model (2026-10-13 / MASTER-10): PRO plan has a 30-day duration.
    If an expired PRO row is found, it lazily evaluates to BASIC (if audience
    passes cap) or FREE.
    """
    row = await repository.get_by_user(session, user_id)
    if row is None:
        return PlanTier.FREE
    expires_at = getattr(row, "expires_at", None)
    if row.plan == PlanTier.PRO and expires_at is not None:
        now = datetime.now(timezone.utc)
        if expires_at <= now:
            cap = await get_free_total_member_cap(session)
            members = await count_total_active_members(session, user_id)
            if cap is not None and members > cap:
                return PlanTier.BASIC
            return PlanTier.FREE
    return row.plan


async def get_plan_details(session: AsyncSession, user_id) -> dict:
    """Detailed plan status including expiration and remaining days."""
    row = await repository.get_by_user(session, user_id)
    now = datetime.now(timezone.utc)
    if row is None:
        return {
            "plan": PlanTier.FREE,
            "expires_at": None,
            "days_left": None,
            "is_active": True,
        }
    plan = row.plan
    expires_at = getattr(row, "expires_at", None)
    days_left = None
    if plan == PlanTier.PRO and expires_at is not None:
        if expires_at > now:
            days_left = max(1, math.ceil((expires_at - now).total_seconds() / 86400))
        else:
            cap = await get_free_total_member_cap(session)
            members = await count_total_active_members(session, user_id)
            plan = PlanTier.BASIC if (cap is not None and members > cap) else PlanTier.FREE
            days_left = 0
    return {
        "plan": plan,
        "expires_at": expires_at,
        "days_left": days_left,
        "is_active": True,
    }


async def set_plan(session: AsyncSession, user_id, plan: PlanTier) -> None:
    await repository.upsert(session, user_id, plan)


async def assign_plan(session: AsyncSession, user_id, plan: PlanTier, *, assigned_by_user_id=None) -> None:
    await set_plan(session, user_id, plan)


# --- Owner model §A1: admin-editable member cap + advertising flag ----------

FREE_TOTAL_MEMBER_CAP_KEY = "free_total_member_cap"
ADS_ENABLED_KEY = "ads_enabled"
DEFAULT_FREE_TOTAL_MEMBER_CAP = 1000


async def get_free_total_member_cap(session: AsyncSession) -> int | None:
    """Max total audience (summed across ALL the creator's khatms) allowed on
    FREE before auto-upgrade to BASIC. Admin-editable on the FREE plan
    definition; falls back to 1000. `None`/0 means "no cap" (never upgrade)."""
    definition = await get_definition(session, PlanTier.FREE)
    if definition is None:
        return DEFAULT_FREE_TOTAL_MEMBER_CAP
    raw = definition.entitlements.get(FREE_TOTAL_MEMBER_CAP_KEY, DEFAULT_FREE_TOTAL_MEMBER_CAP)
    try:
        cap = int(raw)
    except (TypeError, ValueError):
        return DEFAULT_FREE_TOTAL_MEMBER_CAP
    return cap if cap > 0 else None


async def count_total_active_members(session: AsyncSession, creator_user_id) -> int:
    """Total ACTIVE participations across every khatm this creator owns."""
    from sqlalchemy import func, select
    from khatmsaz.modules.khatm.models import Khatm
    from khatmsaz.modules.participation.models import Participation, ParticipationStatus

    stmt = (
        select(func.count())
        .select_from(Participation)
        .join(Khatm, Khatm.id == Participation.khatm_id)
        .where(
            Khatm.creator_user_id == creator_user_id,
            Participation.status == ParticipationStatus.ACTIVE,
        )
    )
    return int((await session.execute(stmt)).scalar_one())


async def ads_enabled_for_creator(session: AsyncSession, creator_user_id) -> bool:
    """Whether خدمتگزاران promo ads should be delivered to this creator's
    audience: only on BASIC (and only if the BASIC definition has ads on).
    FREE (under cap) and PRO never receive ads."""
    plan = await get_plan(session, creator_user_id)
    if plan != PlanTier.BASIC:
        return False
    definition = await get_definition(session, PlanTier.BASIC)
    return bool(definition and definition.entitlements.get(ADS_ENABLED_KEY, True))


async def maybe_autoupgrade_free_to_basic(session: AsyncSession, creator_user_id) -> bool:
    """If a FREE creator's total audience has passed the admin cap, move them to
    BASIC (idempotent — only the FREE→BASIC transition returns True, so the
    caller notifies exactly once). PRO/BASIC are left untouched."""
    if await get_plan(session, creator_user_id) != PlanTier.FREE:
        return False
    cap = await get_free_total_member_cap(session)
    if cap is None:
        return False
    if await count_total_active_members(session, creator_user_id) <= cap:
        return False
    await set_plan(session, creator_user_id, PlanTier.BASIC)
    return True


async def get_definition(session: AsyncSession, plan: PlanTier | str):
    return await repository.get_definition(session, plan)


async def has_feature(session: AsyncSession, user_id, feature_key: str) -> bool:
    """Check an entitlement by key; callers need not branch on plan names."""
    definition = await get_definition(session, await get_plan(session, user_id))
    return bool(definition and definition.enabled and definition.entitlements.get(feature_key, False))


async def get_creation_price(
    session: AsyncSession, user_id, *, fallback_price_toman: int = 0
) -> int:
    """Resolve the authoritative charge for creating one khatm.

    Plan definitions are the source of truth. The fallback keeps deployments
    that predate the plan-definition migration compatible. A usage-based
    definition charges its per-use amount for one creation.
    """
    plan = await get_plan(session, user_id)
    definition = await get_definition(session, plan)
    # Owner model §A5 (2026-09-30): everyone in the ختم‌ساز bot is a creator and
    # may build khatms — creation is never blocked by tier. Only the *price*
    # depends on the plan definition (PRO = free; otherwise the def's price).
    if definition is None:
        return max(0, fallback_price_toman)
    if plan == PlanTier.PRO:
        return 0
    if definition.pricing_mode == PricingMode.USAGE_BASED.value:
        return max(0, definition.unit_price_toman)
    return max(0, definition.price_toman)


async def set_definition(
    session: AsyncSession, *, plan: PlanTier, title: str, pricing_mode: PricingMode,
    price_toman: int, unit_price_toman: int, entitlements: dict
):
    if price_toman < 0 or unit_price_toman < 0:
        raise ValueError("prices cannot be negative")
    normalized_mode = pricing_mode.value if isinstance(pricing_mode, PricingMode) else pricing_mode
    return await repository.upsert_definition(
        session, plan=plan, title=title, pricing_mode=normalized_mode,
        price_toman=price_toman, unit_price_toman=unit_price_toman,
        entitlements=entitlements,
    )


async def get_pro_plan_price(session: AsyncSession) -> int:
    """Return the admin-configured price for upgrading to PRO (to remove ads)."""
    definition = await get_definition(session, PlanTier.PRO)
    if definition is None or not definition.enabled:
        return 0
    return max(0, int(definition.price_toman or 0))


async def purchase_pro_plan(
    session: AsyncSession,
    user_id,
    *,
    coupon_code: str | None = None,
    days: int = _PRO_PLAN_DURATION_DAYS,
):
    """Purchase or renew the 30-day PRO plan from the user's wallet.

    Owner request (2026-10-13 / MASTER-10):
    - PRO plan duration is 30 days.
    - If renewed while still active, adds 30 days additively to current expiration.
    - If purchased afresh or after lapse, starts 30 days from now.
    """
    from khatmsaz.modules.wallet.models import InvoiceKind

    definition = await get_definition(session, PlanTier.PRO)
    if definition is None or not definition.enabled:
        raise PlanFeatureUnavailableError("پلن حرفه‌ای (PRO) در حال حاضر غیرفعال است.")
    price = max(0, int(definition.price_toman or 0))

    row = await repository.get_by_user(session, user_id)
    now = datetime.now(timezone.utc)
    is_renewal = bool(row and row.plan == PlanTier.PRO and row.expires_at and row.expires_at > now)
    action_label = "تمدید ۳۰ روزه" if is_renewal else "ارتقای ۳۰ روزه"

    invoice = None
    if price > 0:
        invoice = await wallet_service.purchase(
            session,
            user_id=user_id,
            gross_amount_toman=price,
            description=f"{action_label} پلن حرفه‌ای ({definition.title})",
            invoice_kind=InvoiceKind.PURCHASE,
            coupon_code=coupon_code,
        )
    user_plan, new_expiry = await repository.extend_pro_plan(session, user_id, days=days)
    return invoice, new_expiry


async def process_plan_expirations_and_reminders(session: AsyncSession, notify) -> dict:
    """Periodic job (run every minute alongside reminder scan):
    1. Sends 7-day warning to users whose PRO plan expires in <= 7 days.
    2. Sends 24-hour warning to users whose PRO plan expires in <= 24 hours.
    3. Downgrades lapsed PRO plans to FREE or BASIC, and notifies users.
    """
    from khatmsaz.modules.identity import service as identity_service

    now = datetime.now(timezone.utc)
    counts = {"reminded_7d": 0, "reminded_24h": 0, "expired": 0}

    # 1. 7-day warnings
    needing_7d = await repository.list_needing_7d_reminder(session, now=now)
    for p in needing_7d:
        identities = await identity_service.list_identities_for_user(session, p.user_id)
        text = (
            "🌱 <b>یادآوری پایان اعتبار پلن حرفه‌ای</b>\n\n"
            "کاربر گرامی، ۷ روز تا پایان اعتبار پلن حرفه‌ای ۳۰ روزه شما باقی مانده است.\n"
            "برای تداوم امکانات پیشرفته، عدم نمایش تبلیغات به اعضا و ابزارهای حرفه‌ای، می‌توانید هم‌اکنون پلن خود را تمدید فرمایید.\n\n"
            "🔄 <b>با تمدید، ۳۰ روز کامل به مهلت فعلی شما افزوده خواهد شد.</b>\n"
            "جهت تمدید، از بخش کیف پول در منوی ربات اقدام فرمایید."
        )
        for ident in identities:
            try:
                await notify(ident.platform.value, ident.subject, text)
            except Exception:
                pass
        await repository.mark_7d_reminded(session, p.user_id)
        counts["reminded_7d"] += 1

    # 2. 24-hour warnings
    needing_24h = await repository.list_needing_24h_reminder(session, now=now)
    for p in needing_24h:
        identities = await identity_service.list_identities_for_user(session, p.user_id)
        text = (
            "⚠️ <b>هشدار پایان اعتبار پلن حرفه‌ای (۲۴ ساعت باقی‌مانده)</b>\n\n"
            "کاربر گرامی، تنها ۲۴ ساعت تا پایان اعتبار پلن حرفه‌ای شما باقی مانده است.\n"
            "در صورت عدم تمدید، ختم‌های شما به پلن عادی منتقل شده و امکانات حرفه‌ای متوقف خواهند شد.\n\n"
            "🔄 با تمدید هم‌اکنون، ۳۰ روز به اعتبار شما اضافه خواهد شد. جهت تمدید از بخش کیف پول اقدام فرمایید. 🌱"
        )
        for ident in identities:
            try:
                await notify(ident.platform.value, ident.subject, text)
            except Exception:
                pass
        await repository.mark_24h_reminded(session, p.user_id)
        counts["reminded_24h"] += 1

    # 3. Lapsed PRO plans
    newly_expired = await repository.list_newly_expired_pro(session, now=now)
    cap = await get_free_total_member_cap(session)
    for p in newly_expired:
        members = await count_total_active_members(session, p.user_id)
        fallback_tier = PlanTier.BASIC if (cap is not None and members > cap) else PlanTier.FREE
        await repository.downgrade_expired_pro(session, p.user_id, fallback_tier)

        identities = await identity_service.list_identities_for_user(session, p.user_id)
        text = (
            "⏳ <b>پایان مهلت اعتبار پلن حرفه‌ای</b>\n\n"
            "کاربر گرامی، مهلت ۳۰ روزه پلن حرفه‌ای شما به پایان رسید و ختم‌های شما به پلن عادی بازگشتند.\n"
            "هر زمان که تمایل داشتید می‌توانید با تمدید پلن، مجدداً از امکانات حرفه‌ای و عدم نمایش تبلیغات بهره‌مند شوید. 🌱"
        )
        for ident in identities:
            try:
                await notify(ident.platform.value, ident.subject, text)
            except Exception:
                pass
        counts["expired"] += 1

    return counts

