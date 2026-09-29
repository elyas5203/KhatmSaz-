"""Quran media registry, reciter whitelist, and user delivery resolution."""

import re
from urllib.parse import urlparse

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.content.models import DevotionalAsset, DevotionalMedia, KhatmReciter, QuranAssetKind, QuranPageAsset
from khatmsaz.modules.khatm.models import ContentDeliveryMode, Khatm
from khatmsaz.modules.khatm.quran_editions import CANONICAL_QURAN_EDITION_ID, QURAN_EDITIONS
from khatmsaz.modules.settings import service as settings_service

SYSTEM_RECITERS = {
    "parhizgar": "شهریار پرهیزگار",
    "minshawi": "محمد صدیق منشاوی",
    "abdulbasit": "عبدالباسط عبدالصمد",
    "husary": "محمود خلیل حصری",
}
# Owner report (2026-09-20): the reciter picker used to offer all four
# SYSTEM_RECITERS, but only Parhizgar's audio is actually registered in the
# library — picking any of the other three silently produced "no audio
# available" for every page. `SYSTEM_RECITERS` itself stays the full
# technical whitelist (whitelisting/fallback logic and its tests still
# exercise all four ids), but `list_reciters()` — the only thing that
# builds the user-facing picker — is restricted to the ones with real
# content. Add an id here once its audio is actually imported.
RECITERS_WITH_REGISTERED_AUDIO = ("parhizgar",)
DEFAULT_RECITER_ID = "parhizgar"
CANONICAL_EDITION_ID = CANONICAL_QURAN_EDITION_ID
DEVOTIONAL_TYPES = {"DUA", "ZIYARAT"}
TELEGRAM_FORWARD_PREFIX = "telegram-forward:"
SALAWAT_SLUG = "salawat"
SALAWAT_TITLE = "صلوات"
SALAWAT_TEXT = "الّلهُمَّ صَلِّ عَلَی مُحَمَّدٍ وَآلِ مُحَمَّدٍ وَعَجِّلْ فَرَجَهُمْ وَالْعَنْ أعْداءَهُم أجْمَعِینَ"


def get_quran_total_pages(khatm: Khatm) -> int:
    """Total page count for a Quran khatm's edition. OPEN QURAN_PAGE khatms
    already store this in `repetition_target` at creation time
    (khatm_workflow/service.py); COMMITMENT ones don't set it, so fall back
    to the edition's own page count."""
    if khatm.repetition_target:
        return khatm.repetition_target
    edition = QURAN_EDITIONS.get(khatm.quran_edition_id)
    return edition["total_pages"] if edition else QURAN_EDITIONS[CANONICAL_EDITION_ID]["total_pages"]

_PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def encode_telegram_forward_ref(source_chat_id: int, source_message_id: int) -> str:
    if source_message_id <= 0:
        raise ValueError("source message id must be positive")
    return f"{TELEGRAM_FORWARD_PREFIX}{source_chat_id}:{source_message_id}"


def decode_telegram_forward_ref(asset_ref: str) -> tuple[int, int] | None:
    if not asset_ref.startswith(TELEGRAM_FORWARD_PREFIX):
        return None
    try:
        chat_id, message_id = asset_ref.removeprefix(TELEGRAM_FORWARD_PREFIX).split(":", 1)
        return int(chat_id), int(message_id)
    except (TypeError, ValueError):
        return None


def parse_quran_channel_caption(caption: str | None) -> tuple[QuranAssetKind, int, int] | None:
    """Parse the source channel's simple Persian page/audio captions.

    Examples: ``صفحه ۳``, ``صفحات ۱ و ۲`` and ``صوت صفحات ۱ و ۲ و ۳``.
    Non-content posts such as juz headings deliberately return ``None``.
    """
    normalized = (caption or "").translate(_PERSIAN_DIGITS).strip()
    if not normalized or "صفح" not in normalized:
        return None
    numbers = [int(value) for value in re.findall(r"\d+", normalized)]
    if not numbers or any(not 1 <= page <= 604 for page in numbers):
        return None
    page_start, page_end = min(numbers), max(numbers)
    if sorted(set(numbers)) != list(range(page_start, page_end + 1)):
        return None
    kind = QuranAssetKind.AUDIO if "صوت" in normalized else QuranAssetKind.IMAGE
    return kind, page_start, page_end


def _validate_page(page_number: int) -> None:
    if not 1 <= page_number <= QURAN_EDITIONS[CANONICAL_EDITION_ID]["total_pages"]:
        raise ValueError("page must be between 1 and 604")


async def register_quran_page_asset(
    session: AsyncSession, *, edition_id: str, page_number: int,
    kind: QuranAssetKind | str, asset_ref: str, reciter_id: str = "",
    asset_platform: str = "TELEGRAM",
) -> QuranPageAsset:
    if edition_id != CANONICAL_EDITION_ID:
        raise ValueError("only the canonical 604-page edition is supported")
    _validate_page(page_number)
    try:
        asset_kind = QuranAssetKind(kind)
    except (TypeError, ValueError):
        raise ValueError("unsupported Quran asset kind") from None
    if asset_kind == QuranAssetKind.AUDIO:
        reciter_id = reciter_id.strip().lower()
        if reciter_id not in SYSTEM_RECITERS:
            raise ValueError("audio asset requires a known reciter")
    else:
        reciter_id = ""
    if not asset_ref.strip():
        raise ValueError("asset_ref is required")
    asset_platform = asset_platform.upper().strip()
    if asset_platform not in {"TELEGRAM", "BALE"}:
        raise ValueError("unsupported asset platform")
    row = QuranPageAsset(
        id=new_id(), edition_id=edition_id, page_number=page_number,
        kind=asset_kind, reciter_id=reciter_id, asset_ref=asset_ref.strip(),
        asset_platform=asset_platform,
    )
    session.add(row)
    await session.flush()
    return row


async def register_telegram_channel_asset_range(
    session: AsyncSession, *, source_chat_id: int, source_message_id: int,
    page_start: int, page_end: int, kind: QuranAssetKind | str,
    reciter_id: str = "parhizgar",
) -> list[QuranPageAsset]:
    """Idempotently map one source-channel post to every page it covers."""
    if page_start > page_end:
        raise ValueError("page_start must not exceed page_end")
    _validate_page(page_start)
    _validate_page(page_end)
    asset_kind = QuranAssetKind(kind)
    if asset_kind not in {QuranAssetKind.IMAGE, QuranAssetKind.AUDIO}:
        raise ValueError("channel source must be IMAGE or AUDIO")
    normalized_reciter = reciter_id.strip().lower() if asset_kind == QuranAssetKind.AUDIO else ""
    if asset_kind == QuranAssetKind.AUDIO and normalized_reciter not in SYSTEM_RECITERS:
        raise ValueError("audio asset requires a known reciter")
    asset_ref = encode_telegram_forward_ref(source_chat_id, source_message_id)
    rows: list[QuranPageAsset] = []
    for page in range(page_start, page_end + 1):
        row = await session.scalar(
            select(QuranPageAsset).where(
                QuranPageAsset.edition_id == CANONICAL_EDITION_ID,
                QuranPageAsset.page_number == page,
                QuranPageAsset.kind == asset_kind,
                QuranPageAsset.reciter_id == normalized_reciter,
                QuranPageAsset.asset_platform == "TELEGRAM",
            )
        )
        if row is None:
            row = QuranPageAsset(
                id=new_id(), edition_id=CANONICAL_EDITION_ID, page_number=page,
                kind=asset_kind, reciter_id=normalized_reciter, asset_ref=asset_ref,
                asset_platform="TELEGRAM",
            )
            session.add(row)
        else:
            row.asset_ref = asset_ref
        rows.append(row)
    await session.flush()
    return rows


async def quran_channel_coverage(session: AsyncSession) -> dict[str, object]:
    """Return exact 604-page coverage and missing pages for channel forwards."""
    result = await session.execute(
        select(QuranPageAsset).where(
            QuranPageAsset.edition_id == CANONICAL_EDITION_ID,
            QuranPageAsset.asset_platform == "TELEGRAM",
            QuranPageAsset.asset_ref.startswith(TELEGRAM_FORWARD_PREFIX),
        )
    )
    image_pages: set[int] = set()
    audio_pages: set[int] = set()
    for row in result.scalars():
        target = audio_pages if row.kind == QuranAssetKind.AUDIO else image_pages
        target.add(row.page_number)
    all_pages = set(range(1, 605))
    return {
        "image_count": len(image_pages), "audio_count": len(audio_pages),
        "missing_images": sorted(all_pages - image_pages),
        "missing_audio": sorted(all_pages - audio_pages),
        "ready": image_pages == all_pages,
    }


async def seed_verified_quran_channel_map(session: AsyncSession) -> dict[str, object]:
    """Idempotently load the repository's verified 604-page source map."""
    from khatmsaz.modules.content.quran_channel_seed import (
        AUDIO_MESSAGE_RANGES, IMAGE_MESSAGE_IDS, SOURCE_CHAT_ID, validate_seed,
    )

    validate_seed()
    for page, message_id in enumerate(IMAGE_MESSAGE_IDS, start=1):
        await register_telegram_channel_asset_range(
            session, source_chat_id=SOURCE_CHAT_ID, source_message_id=message_id,
            page_start=page, page_end=page, kind=QuranAssetKind.IMAGE,
        )
    for page_start, page_end, message_id in AUDIO_MESSAGE_RANGES:
        await register_telegram_channel_asset_range(
            session, source_chat_id=SOURCE_CHAT_ID, source_message_id=message_id,
            page_start=page_start, page_end=page_end, kind=QuranAssetKind.AUDIO,
            reciter_id="parhizgar",
        )
    return await quran_channel_coverage(session)


async def resolve_complete_quran_page_assets(
    session: AsyncSession, *, edition_id: str, page_start: int, page_end: int,
    kind: QuranAssetKind | str, reciter_id: str = "", asset_platform: str = "TELEGRAM"
) -> list[QuranPageAsset] | None:
    """Return an exact contiguous range, or None when any page is missing."""
    if page_start > page_end:
        raise ValueError("page_start must not exceed page_end")
    _validate_page(page_start)
    _validate_page(page_end)
    asset_kind = QuranAssetKind(kind)
    normalized_reciter = reciter_id.strip().lower() if asset_kind == QuranAssetKind.AUDIO else ""
    asset_platform = asset_platform.upper().strip()
    result = await session.execute(
        select(QuranPageAsset)
        .where(
            QuranPageAsset.edition_id == edition_id,
            QuranPageAsset.page_number.between(page_start, page_end),
            QuranPageAsset.kind == asset_kind,
            QuranPageAsset.reciter_id == normalized_reciter,
            QuranPageAsset.asset_platform == asset_platform,
        )
        .order_by(QuranPageAsset.page_number)
    )
    rows = list(result.scalars())
    expected = list(range(page_start, page_end + 1))
    return rows if [row.page_number for row in rows] == expected else None


async def resolve_current_quran_delivery(
    session: AsyncSession, *, khatm: Khatm, user_id, page_start: int, page_end: int,
    asset_platform: str = "TELEGRAM"
) -> dict[str, object]:
    """Resolve all available media for one assigned Quran page range.

    The caller can safely send each returned Telegram ``asset_ref`` directly
    (file id or HTTPS URL). Missing libraries are represented as ``None`` and
    never cause a fabricated or mixed-edition delivery.
    """
    if khatm.quran_edition_id != CANONICAL_EDITION_ID:
        return {"image": None, "audio": None, "text": None, "reciter_id": DEFAULT_RECITER_ID}
    settings = await settings_service.get_or_create(session, user_id)
    reciter_id = await get_effective_reciter(session, khatm.id, user_id)
    mode = getattr(khatm, "content_delivery_mode", ContentDeliveryMode.AUTO.value)
    image = None
    if mode in (ContentDeliveryMode.AUTO.value, ContentDeliveryMode.PHOTO.value):
        image = await resolve_complete_quran_page_assets(
            session, edition_id=CANONICAL_EDITION_ID, page_start=page_start,
            page_end=page_end, kind=QuranAssetKind.IMAGE,
            asset_platform=asset_platform,
        )
    audio = None
    if settings.quran_audio_enabled:
        audio = await resolve_complete_quran_page_assets(
            session, edition_id=CANONICAL_EDITION_ID, page_start=page_start,
                page_end=page_end, kind=QuranAssetKind.AUDIO, reciter_id=reciter_id,
                asset_platform=asset_platform,
        )
    text = None
    if mode in (ContentDeliveryMode.AUTO.value, ContentDeliveryMode.TEXT.value):
        text = await resolve_complete_quran_page_assets(
            session, edition_id=CANONICAL_EDITION_ID, page_start=page_start,
            page_end=page_end, kind=QuranAssetKind.TEXT,
            asset_platform=asset_platform,
        )
    return {
        "image": image,
        "audio": audio,
        "text": text if (settings.translation_enabled or settings.tafsir_enabled) else None,
        "reciter_id": reciter_id,
    }


async def set_content_delivery_mode(
    session: AsyncSession, *, khatm_id, creator_user_id, mode: ContentDeliveryMode | str
) -> ContentDeliveryMode:
    try:
        selected = ContentDeliveryMode(mode.upper() if isinstance(mode, str) else mode)
    except (TypeError, ValueError):
        raise ValueError("unsupported content delivery mode") from None
    khatm = await session.get(Khatm, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id:
        raise ValueError("only the khatm creator can change content delivery mode")
    khatm.content_delivery_mode = selected.value
    await session.flush()
    return selected


async def register_devotional_text(
    session: AsyncSession, *, content_type: str, slug: str, title: str, text_body: str
) -> DevotionalAsset:
    content_type = content_type.upper().strip()
    slug = slug.strip().lower()
    if content_type not in DEVOTIONAL_TYPES:
        raise ValueError("content_type must be DUA or ZIYARAT")
    if not slug or not title.strip() or not text_body.strip():
        raise ValueError("slug, title, and text_body are required")
    row = await session.scalar(select(DevotionalAsset).where(DevotionalAsset.slug == slug))
    if row is None:
        row = DevotionalAsset(id=new_id(), content_type=content_type, slug=slug, title=title.strip())
        session.add(row)
    row.content_type = content_type
    row.title = title.strip()
    row.text_body = text_body.strip()
    row.enabled = True
    await session.flush()
    return row


async def set_salawat_image_url(session: AsyncSession, image_url: str) -> DevotionalAsset:
    """Store the optional admin-managed image for the one fixed Salawat.

    Salawat is deliberately not a selectable devotional/category row.  Its
    wording is fixed by the owner; this asset only gives the admin panel a
    durable place to add or remove an HTTPS image without a deployment.
    """
    image_url = image_url.strip()
    if image_url:
        parsed = urlparse(image_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("salawat image must be a valid HTTP(S) URL")
    row = await session.scalar(select(DevotionalAsset).where(DevotionalAsset.slug == SALAWAT_SLUG))
    if row is None:
        row = DevotionalAsset(
            id=new_id(), content_type="SALAWAT", slug=SALAWAT_SLUG,
            title=SALAWAT_TITLE, text_body=SALAWAT_TEXT,
        )
        session.add(row)
    row.content_type = "SALAWAT"
    row.title = SALAWAT_TITLE
    row.text_body = SALAWAT_TEXT
    row.image_ref = image_url or None
    # A public URL is usable by both Telegram and Bale; delivery intentionally
    # does not restrict this fixed image to one platform.
    row.image_platform = None
    row.enabled = True
    await session.flush()
    return row


async def register_devotional_audio(
    session: AsyncSession, *, slug: str, asset_ref: str, asset_platform: str
) -> DevotionalAsset:
    slug = slug.strip().lower()
    asset_platform = asset_platform.upper().strip()
    if asset_platform not in {"TELEGRAM", "BALE"}:
        raise ValueError("unsupported asset platform")
    row = await session.scalar(select(DevotionalAsset).where(DevotionalAsset.slug == slug))
    if row is None or not row.enabled:
        raise ValueError("enabled devotional asset not found")
    if not asset_ref.strip():
        raise ValueError("asset_ref is required")
    row.audio_ref = asset_ref.strip()
    row.audio_platform = asset_platform
    await session.flush()
    return row


async def register_devotional_image(
    session: AsyncSession, *, slug: str, asset_ref: str, asset_platform: str
) -> DevotionalAsset:
    """Mirrors `register_devotional_audio` — an image of the devotional
    text (owner request, 2026-09-22)."""
    slug = slug.strip().lower()
    asset_platform = asset_platform.upper().strip()
    if asset_platform not in {"TELEGRAM", "BALE"}:
        raise ValueError("unsupported asset platform")
    row = await session.scalar(select(DevotionalAsset).where(DevotionalAsset.slug == slug))
    if row is None or not row.enabled:
        raise ValueError("enabled devotional asset not found")
    if not asset_ref.strip():
        raise ValueError("asset_ref is required")
    row.image_ref = asset_ref.strip()
    row.image_platform = asset_platform
    await session.flush()
    return row


async def _get_enabled_devotional_asset(session: AsyncSession, slug: str) -> DevotionalAsset:
    row = await session.scalar(select(DevotionalAsset).where(DevotionalAsset.slug == slug.strip().lower()))
    if row is None or not row.enabled:
        raise ValueError("enabled devotional asset not found")
    return row


async def add_devotional_audio_variant(
    session: AsyncSession, *, slug: str, asset_ref: str, asset_platform: str,
    reciter_id: str = "", reciter_label: str | None = None,
) -> DevotionalMedia:
    """Owner request (2026-09-22): a dua can have more than one reciter's
    audio (e.g. Ziyarat Ashura with two different reciters) — unlike
    `register_devotional_audio`'s single slot, this adds one more variant
    without overwriting any existing one. `reciter_id=""` (the default)
    is the "unnamed/only reciter" variant — matches old single-slot
    content once it's migrated here, and is what a slug with just one
    audio ever needs."""
    asset = await _get_enabled_devotional_asset(session, slug)
    asset_platform = asset_platform.upper().strip()
    if asset_platform not in {"TELEGRAM", "BALE"}:
        raise ValueError("unsupported asset platform")
    if not asset_ref.strip():
        raise ValueError("asset_ref is required")
    reciter_id = reciter_id.strip().lower()
    row = await session.scalar(
        select(DevotionalMedia).where(
            DevotionalMedia.devotional_asset_id == asset.id, DevotionalMedia.kind == "AUDIO",
            DevotionalMedia.reciter_id == reciter_id, DevotionalMedia.asset_platform == asset_platform,
        )
    )
    if row is None:
        row = DevotionalMedia(
            id=new_id(), devotional_asset_id=asset.id, kind="AUDIO", reciter_id=reciter_id,
            page_number=0, asset_ref=asset_ref.strip(), asset_platform=asset_platform,
        )
        session.add(row)
    else:
        row.asset_ref = asset_ref.strip()
    row.reciter_label = reciter_label or (reciter_id or None)
    await session.flush()
    return row


async def add_devotional_image_page(
    session: AsyncSession, *, slug: str, asset_ref: str, asset_platform: str, page_number: int | None = None,
) -> DevotionalMedia:
    """Owner request (2026-09-22): a dua's image can span more than one
    page (pagination) — unlike `register_devotional_image`'s single slot,
    this adds one more page. `page_number=None` auto-appends after the
    highest existing page (1 if there are none yet)."""
    asset = await _get_enabled_devotional_asset(session, slug)
    asset_platform = asset_platform.upper().strip()
    if asset_platform not in {"TELEGRAM", "BALE"}:
        raise ValueError("unsupported asset platform")
    if not asset_ref.strip():
        raise ValueError("asset_ref is required")
    if page_number is None:
        existing_max = await session.scalar(
            select(func.max(DevotionalMedia.page_number)).where(
                DevotionalMedia.devotional_asset_id == asset.id, DevotionalMedia.kind == "IMAGE",
            )
        )
        page_number = (existing_max or 0) + 1
    row = await session.scalar(
        select(DevotionalMedia).where(
            DevotionalMedia.devotional_asset_id == asset.id, DevotionalMedia.kind == "IMAGE",
            DevotionalMedia.page_number == page_number, DevotionalMedia.asset_platform == asset_platform,
        )
    )
    if row is None:
        row = DevotionalMedia(
            id=new_id(), devotional_asset_id=asset.id, kind="IMAGE", reciter_id="",
            page_number=page_number, asset_ref=asset_ref.strip(), asset_platform=asset_platform,
        )
        session.add(row)
    else:
        row.asset_ref = asset_ref.strip()
    await session.flush()
    return row


async def set_devotional_pdf(
    session: AsyncSession, *, slug: str, asset_ref: str, asset_platform: str,
) -> DevotionalMedia:
    """Owner request (2026-09-22): a dua's full text as a PDF document —
    one slot per (asset, platform), replaced on re-upload."""
    asset = await _get_enabled_devotional_asset(session, slug)
    asset_platform = asset_platform.upper().strip()
    if asset_platform not in {"TELEGRAM", "BALE"}:
        raise ValueError("unsupported asset platform")
    if not asset_ref.strip():
        raise ValueError("asset_ref is required")
    row = await session.scalar(
        select(DevotionalMedia).where(
            DevotionalMedia.devotional_asset_id == asset.id, DevotionalMedia.kind == "PDF",
            DevotionalMedia.asset_platform == asset_platform,
        )
    )
    if row is None:
        row = DevotionalMedia(
            id=new_id(), devotional_asset_id=asset.id, kind="PDF", reciter_id="",
            page_number=0, asset_ref=asset_ref.strip(), asset_platform=asset_platform,
        )
        session.add(row)
    else:
        row.asset_ref = asset_ref.strip()
    await session.flush()
    return row


async def list_devotional_audio_variants(session: AsyncSession, slug: str, asset_platform: str) -> list[DevotionalMedia]:
    asset = await session.scalar(select(DevotionalAsset).where(DevotionalAsset.slug == slug.strip().lower()))
    if asset is None:
        return []
    result = await session.execute(
        select(DevotionalMedia).where(
            DevotionalMedia.devotional_asset_id == asset.id, DevotionalMedia.kind == "AUDIO",
            DevotionalMedia.asset_platform == asset_platform.upper(),
        ).order_by(DevotionalMedia.created_at)
    )
    return list(result.scalars())


async def list_devotional_image_pages(session: AsyncSession, slug: str, asset_platform: str) -> list[DevotionalMedia]:
    asset = await session.scalar(select(DevotionalAsset).where(DevotionalAsset.slug == slug.strip().lower()))
    if asset is None:
        return []
    result = await session.execute(
        select(DevotionalMedia).where(
            DevotionalMedia.devotional_asset_id == asset.id, DevotionalMedia.kind == "IMAGE",
            DevotionalMedia.asset_platform == asset_platform.upper(),
        ).order_by(DevotionalMedia.page_number)
    )
    return list(result.scalars())


async def get_devotional_pdf(session: AsyncSession, slug: str, asset_platform: str) -> DevotionalMedia | None:
    asset = await session.scalar(select(DevotionalAsset).where(DevotionalAsset.slug == slug.strip().lower()))
    if asset is None:
        return None
    return await session.scalar(
        select(DevotionalMedia).where(
            DevotionalMedia.devotional_asset_id == asset.id, DevotionalMedia.kind == "PDF",
            DevotionalMedia.asset_platform == asset_platform.upper(),
        )
    )


async def get_devotional_asset(session: AsyncSession, slug: str) -> DevotionalAsset | None:
    row = await session.scalar(
        select(DevotionalAsset).where(
            DevotionalAsset.slug == slug.strip().lower(), DevotionalAsset.enabled.is_(True)
        )
    )
    return row


async def list_all_devotional_assets(session: AsyncSession) -> list[DevotionalAsset]:
    """Every devotional asset (enabled or not), newest first — for the admin
    management page."""
    result = await session.scalars(
        select(DevotionalAsset).order_by(DevotionalAsset.created_at.desc())
    )
    return list(result)


async def set_devotional_enabled(
    session: AsyncSession, slug: str, enabled: bool
) -> DevotionalAsset | None:
    """Enable/disable a devotional asset by slug (admin toggle). Returns the
    row, or None if the slug does not exist."""
    slug = slug.strip().lower()
    row = await session.scalar(select(DevotionalAsset).where(DevotionalAsset.slug == slug))
    if row is None:
        return None
    row.enabled = enabled
    await session.flush()
    return row


def list_reciters() -> list[tuple[str, str]]:
    return [(rid, SYSTEM_RECITERS[rid]) for rid in RECITERS_WITH_REGISTERED_AUDIO]


async def set_allowed_reciters(
    session: AsyncSession, khatm_id, reciter_ids: list[str]
) -> list[KhatmReciter]:
    normalized = [item.strip().lower() for item in reciter_ids if item.strip()]
    if any(item not in SYSTEM_RECITERS for item in normalized):
        raise ValueError("unknown reciter")
    await session.execute(delete(KhatmReciter).where(KhatmReciter.khatm_id == khatm_id))
    rows = [
        KhatmReciter(id=new_id(), khatm_id=khatm_id, reciter_id=reciter_id, priority=priority)
        for priority, reciter_id in enumerate(dict.fromkeys(normalized))
    ]
    session.add_all(rows)
    await session.flush()
    return rows


async def get_allowed_reciters(session: AsyncSession, khatm_id) -> list[KhatmReciter]:
    result = await session.execute(
        select(KhatmReciter)
        .where(KhatmReciter.khatm_id == khatm_id)
        .order_by(KhatmReciter.priority, KhatmReciter.created_at)
    )
    return list(result.scalars())


async def get_effective_reciter(session: AsyncSession, khatm_id, user_id) -> str:
    """Favorite wins only when allowed; otherwise use whitelist then default."""
    allowed = await get_allowed_reciters(session, khatm_id)
    settings = await settings_service.get_or_create(session, user_id)
    allowed_ids = {row.reciter_id for row in allowed}
    if settings.preferred_reciter in allowed_ids:
        return settings.preferred_reciter
    if allowed:
        return allowed[0].reciter_id
    return DEFAULT_RECITER_ID


async def set_user_favorite(session: AsyncSession, user_id, reciter_id: str) -> None:
    reciter_id = reciter_id.strip().lower()
    if reciter_id not in SYSTEM_RECITERS:
        raise ValueError("unknown reciter")
    settings = await settings_service.get_or_create(session, user_id)
    settings.preferred_reciter = reciter_id
    await session.flush()


async def append_devotional_media_from_message(
    session: AsyncSession, slug: str, message, platform: "Platform | str"  # type: ignore
) -> str | None:
    """Extracts media/text from an aiogram Message and appends it to a devotional asset."""
    from aiogram.types import Message
    msg: Message = message
    platform_val = platform.value if hasattr(platform, "value") else str(platform)
    
    slug = slug.strip().lower()
    asset = await session.scalar(select(DevotionalAsset).where(DevotionalAsset.slug == slug))
    if not asset:
        asset = DevotionalAsset(
            id=new_id(), content_type="DUA", slug=slug, title=slug, text_body=""
        )
        session.add(asset)
        await session.flush()
        
    kind = None
    file_id = None
    
    if msg.photo:
        kind = "IMAGE"
        file_id = msg.photo[-1].file_id
    elif msg.audio:
        kind = "AUDIO"
        file_id = msg.audio.file_id
    elif msg.voice:
        kind = "AUDIO"
        file_id = msg.voice.file_id
    elif msg.document and msg.document.mime_type == "application/pdf":
        kind = "PDF"
        file_id = msg.document.file_id
    elif msg.text:
        text = msg.text.strip()
        if asset.text_body:
            asset.text_body += f"\x1e{text}"
        else:
            asset.text_body = text
        await session.flush()
        return "TEXT"
        
    if kind and file_id:
        media = DevotionalMedia(
            id=new_id(),
            devotional_asset_id=asset.id,
            kind=kind,
            asset_ref=file_id,
            asset_platform=platform_val,
        )
        session.add(media)
        await session.flush()
        return kind
        
    return None
