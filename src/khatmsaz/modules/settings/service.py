"""Settings business logic, plus the "is this participant registered yet"
check that gates joining a khatm for the first time (DOMAIN_MODEL.md §1).
"""

from sqlalchemy.ext.asyncio import AsyncSession
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from khatmsaz.modules.settings import repository
from khatmsaz.modules.settings.models import FontSize, Gender, UserSettings


async def get_or_create(session: AsyncSession, user_id) -> UserSettings:
    settings = await repository.get_by_user(session, user_id)
    if settings is not None:
        return settings
    return await repository.create_for_user(session, user_id)


async def is_registered(session: AsyncSession, user_id) -> bool:
    """A participant is "registered" once they have a contact phone,
    province, city, and gender saved — the short profile DOMAIN_MODEL.md §1
    asks for on first join. Display name is checked separately (it lives on
    `User`, owned by the identity module — see `registration` bot handler)."""
    settings = await repository.get_by_user(session, user_id)
    if settings is None:
        return False
    return bool(settings.contact_phone and settings.province and settings.city and settings.gender)


async def save_profile(
    session: AsyncSession, user_id, *, contact_phone: str, province: str, city: str, gender: Gender
) -> None:
    settings = await get_or_create(session, user_id)
    settings.contact_phone = contact_phone
    settings.province = province
    settings.city = city
    settings.gender = gender
    await session.flush()


async def set_timezone(session: AsyncSession, user_id, timezone_name: str) -> UserSettings:
    """Store only an IANA timezone that Python can resolve."""
    try:
        ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError("unknown timezone") from None
    settings = await get_or_create(session, user_id)
    settings.timezone = timezone_name
    await session.flush()
    return settings


SUPPORTED_LANGUAGES = ("fa", "ar", "en")


async def set_language(session: AsyncSession, user_id, language: str) -> UserSettings:
    """Store one of the locales supported by the bot."""
    normalized = language.strip().lower()
    if normalized not in SUPPORTED_LANGUAGES:
        raise ValueError("unsupported language")
    settings = await get_or_create(session, user_id)
    settings.language = normalized
    settings.language_prompted = True
    await session.flush()
    return settings


async def mark_language_prompted(session: AsyncSession, user_id) -> None:
    """Called even if the user dismisses/ignores the first-run language
    prompt, so they're never asked again on a later /start."""
    settings = await get_or_create(session, user_id)
    settings.language_prompted = True
    await session.flush()


async def set_sms_enabled(session: AsyncSession, user_id, enabled: bool) -> UserSettings:
    """Toggle SMS delivery only when a contact number is available."""
    settings = await get_or_create(session, user_id)
    if enabled and not settings.contact_phone:
        raise ValueError("contact phone required")
    settings.sms_enabled = enabled
    await session.flush()
    return settings


async def set_font_size(session: AsyncSession, user_id, font_size: FontSize | str) -> UserSettings:
    try:
        normalized = FontSize(font_size.upper() if isinstance(font_size, str) else font_size)
    except (TypeError, ValueError):
        raise ValueError("unsupported font size") from None
    settings = await get_or_create(session, user_id)
    settings.font_size = normalized
    await session.flush()
    return settings


async def set_content_option(
    session: AsyncSession, user_id, option: str, enabled: bool
) -> UserSettings:
    field_by_option = {"translation": "translation_enabled", "tafsir": "tafsir_enabled"}
    field = field_by_option.get(option.strip().lower())
    if field is None:
        raise ValueError("unsupported content option")
    settings = await get_or_create(session, user_id)
    setattr(settings, field, enabled)
    await session.flush()
    return settings


async def set_quran_audio_enabled(session: AsyncSession, user_id, enabled: bool) -> UserSettings:
    settings = await get_or_create(session, user_id)
    settings.quran_audio_enabled = enabled
    await session.flush()
    return settings
