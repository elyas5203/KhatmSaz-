"""Business rules for creator messages requiring mandatory moderation."""

from dataclasses import dataclass

from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession

import math

from khatmsaz.modules.broadcast import repository
from khatmsaz.modules.broadcast.models import BroadcastStatus, KhatmBroadcast
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import CreatorDisplayMode, Khatm, KhatmStatus
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.identity.models import PlatformIdentity, Platform
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.settings.models import UserSettings
from khatmsaz.modules.plan import service as plan_service
from khatmsaz.modules.plan.models import PlanTier
from khatmsaz.modules.system_settings import service as system_settings_service
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.models import InvoiceKind

CHANNELS = ("TELEGRAM", "BALE", "SMS")


@dataclass(frozen=True)
class DigitalDestination:
    subject: str
    bot_instance_id: object | None


async def audience_user_ids(
    session: AsyncSession, creator_user_id, *, khatm_id=None,
    province: str | None = None, gender: str | None = None,
) -> list:
    stmt = (
        select(Participation.user_id).distinct()
        .join(Khatm, Khatm.id == Participation.khatm_id)
        .where(Khatm.creator_user_id == creator_user_id, Participation.status == ParticipationStatus.ACTIVE)
    )
    if khatm_id is not None:
        stmt = stmt.where(Participation.khatm_id == khatm_id)
    if province or gender:
        stmt = stmt.join(UserSettings, UserSettings.user_id == Participation.user_id)
    if province:
        stmt = stmt.where(func.lower(UserSettings.province) == province.strip().lower())
    if gender:
        normalized_gender = gender.strip().upper()
        if normalized_gender not in {"MALE", "FEMALE"}:
            raise ValueError("invalid audience gender")
        stmt = stmt.where(UserSettings.gender == normalized_gender)
    return list((await session.execute(stmt)).scalars())


async def channel_policy(session, channel: str) -> tuple[int, int]:
    channel = channel.upper()
    if channel not in CHANNELS:
        raise ValueError("invalid broadcast channel")
    prefix = channel.lower()
    return (
        await system_settings_service.get_int(session, f"broadcast_{prefix}_free_count"),
        await system_settings_service.get_int(session, f"broadcast_{prefix}_price_toman"),
    )


async def channel_package_size(session, channel: str) -> int:
    channel = channel.upper()
    if channel not in CHANNELS:
        raise ValueError("invalid broadcast channel")
    prefix = channel.lower()
    if not hasattr(session, "get") and not hasattr(session, "execute"):
        return 1000
    try:
        size = await system_settings_service.get_int(session, f"broadcast_{prefix}_package_size")
        return size if size > 0 else 1000
    except Exception:
        return 1000


async def per_message_price(session, channel: str) -> int:
    channel = channel.upper()
    if channel not in CHANNELS:
        raise ValueError("invalid broadcast channel")
    prefix = channel.lower()
    if not hasattr(session, "get") and not hasattr(session, "execute"):
        return 150
    try:
        price = await system_settings_service.get_int(session, f"broadcast_{prefix}_per_message_price_toman")
        return price if price > 0 else 150
    except Exception:
        return 150


async def submit(
    session: AsyncSession, *, khatm_id, creator_user_id, body: str, channel: str = "TELEGRAM",
    media_type: str | None = None, media_file_id: str | None = None,
    province: str | None = None, gender: str | None = None,
    cost_override: int | None = None,
) -> KhatmBroadcast:
    # Owner §A2 (2026-09-30): a promo message can be text OR media (photo/video/
    # voice/document) with an optional caption. Media file_ids are platform-
    # specific, so store the uploaded one under the column matching the channel.
    body = (body or "").strip()
    has_media = bool(media_type and media_type != "text" and media_file_id)
    if not has_media and not body:
        raise ValueError("broadcast needs text or media")
    if len(body) > 1000:
        raise ValueError("broadcast body must be at most 1000 characters")
    channel = channel.upper()
    if channel not in CHANNELS:
        raise ValueError("invalid broadcast channel")
    if channel == "SMS" and has_media:
        raise ValueError("SMS broadcasts cannot carry media")
    if khatm_id is not None:
        khatm = await khatm_service.get_khatm(session, khatm_id)
        if khatm is None or khatm.creator_user_id != creator_user_id or khatm.status != KhatmStatus.ACTIVE:
            raise ValueError("only the creator of an active khatm may submit a broadcast")
    province = (province or "").strip() or None
    gender = (gender or "").strip().upper() or None
    users = await audience_user_ids(
        session, creator_user_id, khatm_id=khatm_id, province=province, gender=gender,
    )
    if not users:
        raise ValueError("broadcast audience is empty")
    # MASTER-31 & MASTER-38: Broadcast entitlement is wallet-balance-based.

    if cost_override is not None:
        cost = max(0, cost_override)
        description = f"هزینه ارسال پیام گروهی برای {len(users):,} مخاطب فعال"
    else:
        # Calculate dynamic package count and total cost
        policy = await channel_policy(session, channel)
        if len(policy) >= 3:
            _free_count, unit_price, package_size = policy[0], policy[1], policy[2]
        else:
            _free_count, unit_price = policy[0], policy[1]
            package_size = await channel_package_size(session, channel)

        if package_size <= 0 or not isinstance(package_size, int):
            package_size = 1000
        if unit_price <= 0 or not isinstance(unit_price, int):
            unit_price = 50_000 if channel in {"TELEGRAM", "BALE"} else 100_000

        packages_count = math.ceil(len(users) / package_size)
        cost = packages_count * unit_price
        pkg_label = "۱۰۰۰" if package_size == 1000 else f"{package_size:,}"
        description = f"هزینه ارسال پیام گروهی ({packages_count} بسته {pkg_label} نفری برای {len(users)} مخاطب)"

    invoice = None
    if cost > 0:
        invoice = await wallet_service.spend(
            session,
            user_id=creator_user_id,
            amount=cost,
            description=description,
            invoice_kind=InvoiceKind.PURCHASE,
        )
    tg_media = media_file_id if (has_media and channel == "TELEGRAM") else None
    bale_media = media_file_id if (has_media and channel == "BALE") else None
    broadcast = await repository.create(
        session, khatm_id=khatm_id, creator_user_id=creator_user_id, body=body,
        target_scope="KHATM" if khatm_id else "ALL", channel=channel,
        audience_count=len(users), cost_toman=cost,
        target_province=province, target_gender=gender,
        media_type=media_type if has_media else None,
        media_file_id_telegram=tg_media, media_file_id_bale=bale_media,
    )
    if invoice is not None and getattr(broadcast, "id", None) is not None:
        await wallet_service.bind_invoice_resource(session, invoice.id, str(broadcast.id))
    return broadcast


async def audience_destinations(session: AsyncSession, item: KhatmBroadcast):
    creator_user_id = getattr(item, "creator_user_id", None)
    if not creator_user_id:
        return []
    user_ids = await audience_user_ids(
        session, creator_user_id, khatm_id=getattr(item, "khatm_id", None),
        province=getattr(item, "target_province", None), gender=getattr(item, "target_gender", None),
    )
    channel = getattr(item, "channel", "TELEGRAM")
    if channel == "SMS":
        result = await session.execute(select(UserSettings.contact_phone).where(
            UserSettings.user_id.in_(user_ids), UserSettings.contact_phone.isnot(None)
        ))
        return list(dict.fromkeys(phone for phone in result.scalars() if phone))
    try:
        platform = Platform(channel)
    except Exception:
        platform = Platform.TELEGRAM
    stmt = (
        select(PlatformIdentity.subject, Participation.joined_via_bot_instance_id)
        .join(Participation, Participation.user_id == PlatformIdentity.user_id)
        .join(Khatm, Khatm.id == Participation.khatm_id)
        .where(
            PlatformIdentity.user_id.in_(user_ids),
            PlatformIdentity.platform == platform,
            Participation.status == ParticipationStatus.ACTIVE,
            Khatm.creator_user_id == item.creator_user_id,
        )
    )
    if item.khatm_id is not None:
        stmt = stmt.where(Participation.khatm_id == item.khatm_id)
    result = await session.execute(stmt)
    return [
        DigitalDestination(subject=subject, bot_instance_id=bot_instance_id)
        for subject, bot_instance_id in dict.fromkeys(result.all())
    ]


async def sender_display_name(session: AsyncSession, item: KhatmBroadcast) -> str:
    """Respect the creator name mode chosen for the targeted khatm."""
    creator_id = getattr(item, "creator_user_id", None)
    creator = await identity_service.find_by_id(session, creator_id) if creator_id else None
    full_name = creator.display_name if creator and creator.display_name else "سازندهٔ ختم"
    khatm_id = getattr(item, "khatm_id", None)
    if khatm_id is None:
        return full_name
    khatm = await khatm_service.get_khatm(session, khatm_id)
    if khatm is None:
        return full_name
    mode = getattr(khatm, "creator_display_mode", CreatorDisplayMode.FULL_NAME.value)
    if mode == CreatorDisplayMode.PSEUDONYM.value:
        return khatm.creator_pseudonym or "سازندهٔ ختم"
    if mode == CreatorDisplayMode.ANONYMOUS.value:
        return "سازندهٔ ختم"
    if mode == CreatorDisplayMode.FIRST_NAME.value:
        return full_name.split()[0]
    return full_name


async def get(session: AsyncSession, broadcast_id) -> KhatmBroadcast | None:
    return await repository.get_by_id(session, broadcast_id)


async def list_pending(session: AsyncSession) -> list[KhatmBroadcast]:
    return await repository.list_pending(session)


async def approve(session: AsyncSession, broadcast_id, note: str | None = None) -> KhatmBroadcast:
    item = await repository.get_by_id(session, broadcast_id)
    if item is None or item.status != BroadcastStatus.PENDING:
        raise ValueError("broadcast is not pending")
    await repository.mark_reviewed(session, item, BroadcastStatus.APPROVED, note)
    return item


async def reject(session: AsyncSession, broadcast_id, note: str | None = None) -> KhatmBroadcast:
    item = await repository.get_by_id(session, broadcast_id)
    if item is None or item.status != BroadcastStatus.PENDING:
        raise ValueError("broadcast is not pending")
    await repository.mark_reviewed(session, item, BroadcastStatus.REJECTED, note)
    # DEC-PY-0121 / MASTER-10: Refund wallet if message is rejected by admin
    if item.cost_toman > 0:
        refunded = await wallet_service.refund_purchase_invoice(
            session,
            user_id=item.creator_user_id,
            kind=InvoiceKind.PURCHASE,
            resource_ref=str(item.id),
            description=f"بازگشت وجه پیام گروهی رد شده (کد: {str(item.id)[:8]})",
        )
        if refunded is None:
            await wallet_service.add_cash(
                session,
                user_id=item.creator_user_id,
                amount=item.cost_toman,
                description=f"بازگشت وجه پیام گروهی رد شده (کد: {str(item.id)[:8]})",
                ref=f"REFUND-BC-{str(item.id)[:8]}",
            )
    return item


async def mark_sent(session: AsyncSession, item: KhatmBroadcast) -> None:
    await repository.mark_sent(session, item)
