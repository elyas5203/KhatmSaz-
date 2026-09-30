"""Business rules for creator messages requiring mandatory moderation."""

from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.broadcast import repository
from khatmsaz.modules.broadcast.models import BroadcastStatus, KhatmBroadcast
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.identity.models import PlatformIdentity, Platform
from khatmsaz.modules.settings.models import UserSettings
from khatmsaz.modules.plan import service as plan_service
from khatmsaz.modules.plan.models import PlanTier
from khatmsaz.modules.system_settings import service as system_settings_service

CHANNELS = ("TELEGRAM", "BALE", "SMS")


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


async def submit(
    session: AsyncSession, *, khatm_id, creator_user_id, body: str, channel: str = "TELEGRAM",
    media_type: str | None = None, media_file_id: str | None = None,
    province: str | None = None, gender: str | None = None,
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
    _free_count, price = await channel_policy(session, channel)
    if channel in {"TELEGRAM", "BALE"}:
        plan = await plan_service.get_plan(session, creator_user_id)
        used = await repository.count_lifetime_digital_for_creator(session, creator_user_id)
        if plan != PlanTier.PRO and (len(users) >= 1000 or used >= 2):
            raise plan_service.PlanFeatureUnavailableError(
                "more than two digital broadcasts or an audience of 1000+ requires PRO"
            )
        cost = 0
    else:
        # SMS is paid from the first request. Operations controls its price.
        cost = price
    tg_media = media_file_id if (has_media and channel == "TELEGRAM") else None
    bale_media = media_file_id if (has_media and channel == "BALE") else None
    return await repository.create(
        session, khatm_id=khatm_id, creator_user_id=creator_user_id, body=body,
        target_scope="KHATM" if khatm_id else "ALL", channel=channel,
        audience_count=len(users), cost_toman=cost,
        target_province=province, target_gender=gender,
        media_type=media_type if has_media else None,
        media_file_id_telegram=tg_media, media_file_id_bale=bale_media,
    )


async def audience_destinations(session: AsyncSession, item: KhatmBroadcast):
    user_ids = await audience_user_ids(
        session, item.creator_user_id, khatm_id=item.khatm_id,
        province=item.target_province, gender=item.target_gender,
    )
    if item.channel == "SMS":
        result = await session.execute(select(UserSettings.contact_phone).where(
            UserSettings.user_id.in_(user_ids), UserSettings.contact_phone.isnot(None)
        ))
        return list(dict.fromkeys(phone for phone in result.scalars() if phone))
    platform = Platform(item.channel)
    result = await session.execute(select(PlatformIdentity.subject).where(
        PlatformIdentity.user_id.in_(user_ids), PlatformIdentity.platform == platform
    ))
    return list(dict.fromkeys(result.scalars()))


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
    return item


async def mark_sent(session: AsyncSession, item: KhatmBroadcast) -> None:
    await repository.mark_sent(session, item)
