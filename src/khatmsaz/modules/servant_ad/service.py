"""خدمتگزاران system-ad service (owner §A4).

Reads/writes the single active system ad in the generic system-settings KV
store, computes the BASIC-tier audience, and delivers the ad once per user
(admin-initiated). Kept dependency-light: delivery is injected as callables so
this module never imports the bot layer.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.identity.models import Platform, PlatformIdentity
from khatmsaz.modules.khatm.models import Khatm
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.plan import service as plan_service
from khatmsaz.modules.system_settings import repository as kv

_TEXT = "servant_ad_text"
_MEDIA_TYPE = "servant_ad_media_type"
_MEDIA_TG = "servant_ad_media_telegram"
_MEDIA_BALE = "servant_ad_media_bale"
_ENABLED = "servant_ad_enabled"

# (platform_value, subject, text, media_type|None, media_file_id|None) -> bool
SendFn = Callable[..., Awaitable[bool]]


async def get_ad(session: AsyncSession) -> dict:
    return {
        "text": (await kv.get(session, _TEXT)) or "",
        "media_type": (await kv.get(session, _MEDIA_TYPE)) or "",
        "media_telegram": (await kv.get(session, _MEDIA_TG)) or "",
        "media_bale": (await kv.get(session, _MEDIA_BALE)) or "",
        "enabled": (await kv.get(session, _ENABLED)) == "1",
    }


async def set_ad(
    session: AsyncSession, *, text: str, enabled: bool,
    media_type: str = "", media_telegram: str = "", media_bale: str = "",
) -> None:
    text = (text or "").strip()
    if len(text) > 1500:
        raise ValueError("servant ad text too long")
    await kv.set(session, _TEXT, text)
    await kv.set(session, _MEDIA_TYPE, (media_type or "").strip())
    await kv.set(session, _MEDIA_TG, (media_telegram or "").strip())
    await kv.set(session, _MEDIA_BALE, (media_bale or "").strip())
    await kv.set(session, _ENABLED, "1" if enabled else "0")


async def _basic_creator_ids(session: AsyncSession) -> set:
    """Creators who currently have ads enabled (BASIC tier)."""
    creator_ids = set(
        (await session.execute(select(Khatm.creator_user_id).distinct())).scalars()
    )
    return {
        cid for cid in creator_ids
        if await plan_service.ads_enabled_for_creator(session, cid)
    }


async def _targets(session: AsyncSession) -> list[tuple[str, str]]:
    """Distinct (platform_value, subject) for every audience member of a
    BASIC-tier creator. Deduped so one person is messaged once even if they
    belong to several such creators' khatms."""
    basic = await _basic_creator_ids(session)
    if not basic:
        return []
    user_ids = set(
        (await session.execute(
            select(Participation.user_id)
            .join(Khatm, Khatm.id == Participation.khatm_id)
            .where(
                Khatm.creator_user_id.in_(basic),
                Participation.status == ParticipationStatus.ACTIVE,
            )
            .distinct()
        )).scalars()
    )
    if not user_ids:
        return []
    rows = (await session.execute(
        select(PlatformIdentity.platform, PlatformIdentity.subject)
        .where(PlatformIdentity.user_id.in_(user_ids))
    )).all()
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []
    for platform, subject in rows:
        pv = platform.value if isinstance(platform, Platform) else str(platform)
        key = (pv, subject)
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


async def audience_size(session: AsyncSession) -> int:
    return len(await _targets(session))


async def send_now(session: AsyncSession, send: SendFn) -> int:
    """Deliver the active ad to the BASIC audience once each. Returns the number
    of successful deliveries. Raises ValueError if the ad is disabled/empty."""
    ad = await get_ad(session)
    if not ad["enabled"]:
        raise ValueError("servant ad is disabled")
    if not ad["text"] and not ad["media_type"]:
        raise ValueError("servant ad is empty")
    delivered = 0
    for platform_value, subject in await _targets(session):
        media_file_id = ad["media_telegram"] if platform_value == "TELEGRAM" else ad["media_bale"]
        ok = await send(
            platform_value, subject, ad["text"],
            ad["media_type"] or None, media_file_id or None,
        )
        if ok:
            delivered += 1
    return delivered
