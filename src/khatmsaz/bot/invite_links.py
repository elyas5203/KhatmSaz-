"""Shared invite-link builder for the multi-bot architecture.

A Khatm's invite links must point at the correct **member bot** (category +
language), not at the creator bot or only at the web landing page. Both the
creation wizard (`create_khatm.finish_invite_links`) and the "QR دعوت" button
in khatm management (`my_khatms.khatm_qr`) build the same links — this module
is the single source of truth so the two never drift apart.
"""
from __future__ import annotations

from khatmsaz.core.bot_registry import get_registry
from khatmsaz.modules.bot_registry import service as bot_registry_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.khatm.models import Khatm
from khatmsaz.modules.khatm_category import service as category_service

_LANG_LABELS = {"fa": "🇮🇷 فارسی", "ar": "🇸🇦 عربی", "en": "🇬🇧 انگلیسی"}

# Arabic and English member bots are temporarily hidden until those translations & flows are finalized.
ACTIVE_INVITE_LANGUAGES: tuple[str, ...] = ("fa",)


async def resolve_khatm_category_value(session, khatm: Khatm) -> str:
    """Return the BotCategory string ("QURAN", "SALAWAT", ...) for a khatm."""
    category = None
    if khatm.content_category_id:
        category = await category_service.get(session, khatm.content_category_id)
    return bot_registry_service.resolve_bot_category(khatm, category).value


def build_member_invite_links(
    khatm_bot_cat: str,
    token: str,
    *,
    langs: list[str] | None = None,
    plat_choice: str = "ALL",
    include_inactive_langs: bool = False,
) -> dict[str, dict[str, str]]:
    """Build member-bot deep links for one khatm token.

    Returns an ordered dict keyed by language code, each value a dict with
    optional "telegram"/"bale" deep-link URLs. Languages with no configured &
    active member bot for this category are simply absent.

    Arabic and English are temporarily hidden (ACTIVE_INVITE_LANGUAGES = ("fa",))
    unless include_inactive_langs=True is explicitly set.
    """
    registry = get_registry()
    by_lang: dict[str, dict[str, str]] = {}
    if langs is not None:
        target_langs = langs if include_inactive_langs else [l for l in langs if l in ACTIVE_INVITE_LANGUAGES]
    else:
        target_langs = list(ACTIVE_INVITE_LANGUAGES) if not include_inactive_langs else None

    for bot in registry.member_bots():
        b_cat = getattr(bot, "khatmsaz_category", None)
        b_lang = getattr(bot, "khatmsaz_language", None)
        b_username = getattr(bot, "khatmsaz_username", None)
        platform = getattr(bot, "khatmsaz_platform", None)
        if b_cat != khatm_bot_cat or not b_lang or not b_username:
            continue
        if target_langs is not None and b_lang not in target_langs:
            continue
        if plat_choice != "ALL" and platform and platform.value != plat_choice:
            continue
        entry = by_lang.setdefault(b_lang, {})
        if platform == Platform.TELEGRAM:
            entry["telegram"] = f"https://t.me/{b_username}?start=join_{token}"
        elif platform == Platform.BALE:
            entry["bale"] = f"https://ble.ir/{b_username}?start=join_{token}"
    return by_lang


def format_invite_lines(by_lang: dict[str, dict[str, str]]) -> str:
    """Render member-bot links as a readable, multi-line Persian block.

    When only one language is present (e.g. Persian only), the language label
    header is omitted to keep the message clean and focused. When multiple
    languages are present, each language section is prefixed with a label header.
    """
    lines: list[str] = []
    show_headers = len(by_lang) > 1
    for lang_code, urls in by_lang.items():
        if show_headers:
            lines.append(f"\u200f{_LANG_LABELS.get(lang_code, lang_code)}:")
        if urls.get("telegram"):
            lines.append(f"▫️ تلگرام: {urls['telegram']}")
        if urls.get("bale"):
            lines.append(f"▫️ بله: {urls['bale']}")
        if show_headers:
            lines.append("")
    return "\n".join(lines).strip()


def pick_primary_link(
    by_lang: dict[str, dict[str, str]],
    *,
    preferred_lang: str = "fa",
    preferred_platform: str = "TELEGRAM",
) -> str | None:
    """Choose one link to encode in a QR: prefer the creator's language and
    platform, then fall back to any available member-bot link."""
    plat_key = "telegram" if preferred_platform == "TELEGRAM" else "bale"
    if preferred_lang in by_lang and by_lang[preferred_lang].get(plat_key):
        return by_lang[preferred_lang][plat_key]
    # Any link for the preferred language, either platform.
    if preferred_lang in by_lang:
        for value in by_lang[preferred_lang].values():
            return value
    # Any link at all.
    for urls in by_lang.values():
        for value in urls.values():
            return value
    return None


def build_web_invite_url(token: str, khatm_bot_cat: str | None = None) -> str:
    """Build a primary invite URL for a token.
    If khatm_bot_cat is provided and matching member bots exist, returns the primary Telegram link.
    Otherwise falls back to any available Telegram member bot or /join/{token}.
    """
    try:
        if khatm_bot_cat:
            by_lang = build_member_invite_links(khatm_bot_cat, token)
            primary = pick_primary_link(by_lang, preferred_lang="fa", preferred_platform="TELEGRAM")
            if primary:
                return primary
        registry = get_registry()
        for bot in registry.member_bots():
            b_lang = getattr(bot, "khatmsaz_language", None)
            if b_lang and b_lang not in ACTIVE_INVITE_LANGUAGES:
                continue
            username = getattr(bot, "khatmsaz_username", None)
            platform = getattr(bot, "khatmsaz_platform", None)
            if username and platform == Platform.TELEGRAM:
                return f"https://t.me/{username}?start=join_{token}"
    except Exception:
        pass
    return f"/join/{token}"
