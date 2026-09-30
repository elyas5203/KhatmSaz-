"""Plan business logic. A missing row means FREE — never create a row just
to read someone's plan (DOMAIN_MODEL.md §7: keep this cheap and lazy)."""

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.plan import repository
from khatmsaz.modules.plan.models import PlanTier, PricingMode
from khatmsaz.modules.wallet import service as wallet_service


class PlanFeatureUnavailableError(Exception):
    """The active plan does not permit the requested feature."""


async def get_plan(session: AsyncSession, user_id) -> PlanTier:
    """The user's STORED plan tier — FREE / BASIC / PRO (missing row = FREE).

    Owner model (OWNER_SPEC_MASTER §A, 2026-09-30): the tier is a real stored
    state, not derived from wallet funds. FREE auto-upgrades to BASIC when the
    creator's total audience passes the admin cap (`maybe_autoupgrade_free_to_basic`),
    and PRO is reached by an explicit purchase. Reads stay cheap: a missing
    `UserPlan` row means FREE and we never create one just to read it.
    """
    row = await repository.get_by_user(session, user_id)
    return row.plan if row is not None else PlanTier.FREE


async def set_plan(session: AsyncSession, user_id, plan: PlanTier) -> None:
    await repository.upsert(session, user_id, plan)


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
