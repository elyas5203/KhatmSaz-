"""The one place non-handler code touches aiogram `Bot` instances.

`reminder_engine.service` is platform-agnostic by design (see its
docstring) — it calls a plain `notify(platform_value, chat_id, text)`
callback without knowing what a `Bot` even is. This module builds that
callback for the real Telegram/Bale bot instances built at startup, and
exposes it as a process-wide singleton (`get_notify_fn`) so other places
that need to message a user on *whichever* platform they're on — not
necessarily the platform of the update currently being handled, e.g.
notifying someone promoted off a waiting list who might be on a different
platform than the person who just left — can reuse the same platform-
routing logic instead of reaching for `callback.message.bot` (which is only
correct when the recipient is on the same platform as the triggering event).

`send_with_keyboard` is the same idea but for the rarer case of needing an
inline keyboard on a cross-platform notification (e.g. a creator's
approve/reject buttons for a leave request — see `bot/handlers/leave.py`).
Kept as a second function rather than widening `NotifyFn` everywhere: most
callers only ever need plain text, and changing that shared type would
touch every existing call site for one feature's sake.
"""

import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup

from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.reminder_engine.service import NotifyFn

logger = logging.getLogger("khatmsaz")

_bots_by_platform: dict[Platform, Bot] = {}
_notify_fn: NotifyFn | None = None
_send_quran_pages_fn = None


def build_notify_fn(bots_by_platform: dict[Platform, Bot]) -> NotifyFn:
    global _bots_by_platform
    _bots_by_platform = bots_by_platform

    async def notify(platform_value: str, chat_id: str, text: str, *, bot_instance_id=None) -> None:
        from khatmsaz.core.bot_registry import get_registry
        registry = get_registry()
        
        # bot_instance_id records the member bot a participant joined through —
        # but a user can have identities on BOTH platforms while joining via a
        # single-platform member bot. Only route through that member bot for the
        # matching platform; for any other platform fall back to that platform's
        # creator bot, otherwise the message is sent from the wrong-platform bot
        # and silently fails to reach the user (they'd get no reminder at all).
        bot = None
        if bot_instance_id:
            candidate = registry.get_by_instance_id(bot_instance_id)
            if candidate is not None and getattr(candidate, "khatmsaz_platform", None) == Platform(platform_value):
                bot = candidate
            elif candidate is not None:
                # Never route a Telegram member-bot id to a Bale identity (or
                # vice versa), and do not duplicate this member reminder via a
                # creator bot on a second linked identity.
                return
        if bot is None:
            bot = registry.get_creator_bot(Platform(platform_value))

        if not bot:
            logger.warning("No bot for %s/%s", platform_value, bot_instance_id)
            return
        try:
            await bot.send_message(chat_id=int(chat_id), text=text)
        except Exception:
            logger.warning("Failed to deliver message to %s:%s", platform_value, chat_id, exc_info=True)

    global _notify_fn
    _notify_fn = notify
    return notify


def get_notify_fn() -> NotifyFn:
    if _notify_fn is None:
        raise RuntimeError("notify_fn not built yet — bootstrap.py must call build_notify_fn() first")
    return _notify_fn


def build_send_quran_pages_fn(bots_by_platform: dict[Platform, Bot]):
    """Builds the callback `reminder_engine.service.deliver_due_open_quran_reading`
    uses to actually deliver Quran page content (image/audio/text) for the
    open-Quran-reading daily auto-send — see BACKLOG.md/PROJECT_STATE.md
    2026-09-21. Mirrors `bot/handlers/portions.py::_send_registered_assets`;
    duplicated rather than imported because `portions.py` is a bot handler
    module the platform-agnostic `reminder_engine` must not depend on."""
    global _bots_by_platform
    _bots_by_platform = bots_by_platform

    async def send_quran_pages(session, platform_value: str, chat_id: str, *, khatm, user_id, page_start: int, page_end: int, bot_instance_id=None) -> None:
        from khatmsaz.core.bot_registry import get_registry
        registry = get_registry()
        
        if bot_instance_id:
            candidate = registry.get_by_instance_id(bot_instance_id)
            if candidate is not None and getattr(candidate, "khatmsaz_platform", None) != Platform(platform_value):
                return
            bot = candidate
        else:
            bot = registry.get_creator_bot(Platform(platform_value))
        if bot is None:
            return
        delivery = await content_service.resolve_current_quran_delivery(
            session, khatm=khatm, user_id=user_id, page_start=page_start, page_end=page_end,
            asset_platform=platform_value,
        )
        for assets, kind in ((delivery["image"], "image"), (delivery["audio"], "audio"), (delivery["text"], "text")):
            seen: set[str] = set()
            for asset in assets or []:
                if asset.asset_ref in seen:
                    continue
                seen.add(asset.asset_ref)
                try:
                    forward_source = content_service.decode_telegram_forward_ref(asset.asset_ref)
                    if forward_source is not None:
                        source_chat_id, source_message_id = forward_source
                        await bot.forward_message(
                            chat_id=int(chat_id), from_chat_id=source_chat_id, message_id=source_message_id,
                        )
                    elif kind == "image":
                        await bot.send_photo(chat_id=int(chat_id), photo=asset.asset_ref)
                    elif kind == "audio":
                        await bot.send_audio(chat_id=int(chat_id), audio=asset.asset_ref)
                    else:
                        await bot.send_message(chat_id=int(chat_id), text=asset.asset_ref)
                except Exception:
                    logger.warning(
                        "Failed to deliver Quran asset to %s:%s", platform_value, chat_id, exc_info=True
                    )

    global _send_quran_pages_fn
    _send_quran_pages_fn = send_quran_pages
    return send_quran_pages


from aiogram.types import ReplyKeyboardMarkup
async def send_with_keyboard(
    platform_value: str, chat_id: str, text: str, reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup, *, bot_instance_id=None
) -> bool:
    from khatmsaz.core.bot_registry import get_registry
    registry = get_registry()
    if bot_instance_id:
        candidate = registry.get_by_instance_id(bot_instance_id)
        if candidate is not None and getattr(candidate, "khatmsaz_platform", None) != Platform(platform_value):
            return False
        bot = candidate
    else:
        bot = registry.get_creator_bot(Platform(platform_value))
    if bot is None:
        return False
    try:
        await bot.send_message(chat_id=int(chat_id), text=text, reply_markup=reply_markup)
        return True
    except Exception:
        logger.warning(
            "Failed to deliver keyboard message to %s:%s", platform_value, chat_id, exc_info=True
        )
        return False


async def send_media(
    platform_value: str, chat_id: str, media_type: str, file_id: str,
    caption: str | None = None, *, bot_instance_id=None,
) -> bool:
    """Deliver a photo/video/voice/document by file_id (owner §A2 promo media).
    file_ids are platform-specific — the caller must pass one captured on the
    same platform. Best-effort; returns True on success."""
    from khatmsaz.core.bot_registry import get_registry
    registry = get_registry()
    if bot_instance_id:
        bot = registry.get_by_instance_id(bot_instance_id)
        if bot is not None and getattr(bot, "khatmsaz_platform", None) != Platform(platform_value):
            bot = None
    else:
        bot = registry.get_creator_bot(Platform(platform_value))
    if bot is None:
        return False
    try:
        cid = int(chat_id)
        if media_type == "photo":
            await bot.send_photo(chat_id=cid, photo=file_id, caption=caption or None)
        elif media_type == "video":
            await bot.send_video(chat_id=cid, video=file_id, caption=caption or None)
        elif media_type == "voice":
            await bot.send_voice(chat_id=cid, voice=file_id, caption=caption or None)
        elif media_type == "document":
            await bot.send_document(chat_id=cid, document=file_id, caption=caption or None)
        else:
            await bot.send_message(chat_id=cid, text=caption or "")
        return True
    except Exception:
        logger.warning("Failed to deliver media to %s:%s", platform_value, chat_id, exc_info=True)
        return False


async def send_devotional_content(
    session, platform_value: str, chat_id: str, *, khatm, lang: str,
    bot_instance_id=None,
) -> bool:
    """Send the configured image/PDF/text immediately before a reminder."""
    from khatmsaz.core.bot_registry import get_registry
    from khatmsaz.bot.handlers.devotional import deliver_devotional_media
    from khatmsaz.core.devotional_images import resolve_devotional_image_ref
    from khatmsaz.config import get_settings
    from khatmsaz.modules.khatm_category import service as category_service

    registry = get_registry()
    platform = Platform(platform_value)
    bot = registry.get_by_instance_id(bot_instance_id) if bot_instance_id else registry.get_creator_bot(platform)
    if bot is None or getattr(bot, "khatmsaz_platform", platform) != platform:
        return False

    class _TargetMessage:
        def __init__(self):
            self.bot = bot

        async def answer(self, text, **kwargs):
            return await bot.send_message(chat_id=int(chat_id), text=text, **kwargs)

        async def answer_photo(self, photo, **kwargs):
            return await bot.send_photo(chat_id=int(chat_id), photo=photo, **kwargs)

        async def answer_document(self, document, **kwargs):
            return await bot.send_document(chat_id=int(chat_id), document=document, **kwargs)

        async def answer_audio(self, audio, **kwargs):
            return await bot.send_audio(chat_id=int(chat_id), audio=audio, **kwargs)

    target = _TargetMessage()
    try:
        if getattr(khatm, "description", None):
            await target.answer(khatm.description)
            return True

        category = None
        slug = content_service.SALAWAT_SLUG
        if khatm.content_category_id:
            category = await category_service.get(session, khatm.content_category_id)
            slug = category.devotional_slug if category else None

        sent = False
        if category and category.image_url:
            settings = get_settings()
            image_url = resolve_devotional_image_ref(
                category.image_url,
                public_base_url=settings.admin_web_base_url or settings.public_web_base_url,
            )
            if image_url:
                await target.answer_photo(image_url)
                sent = True

        if slug is None:
            if not sent and category and category.body_text:
                await target.answer(category.body_text)
                sent = True
            return sent

        asset = await content_service.get_devotional_asset(session, slug)
        if asset is None:
            if not sent and category and category.body_text:
                await target.answer(category.body_text)
                return True
            return sent

        if slug == content_service.SALAWAT_SLUG and asset.image_ref and asset.image_platform is None:
            settings = get_settings()
            image_url = resolve_devotional_image_ref(
                asset.image_ref,
                public_base_url=settings.admin_web_base_url or settings.public_web_base_url,
            )
            if image_url:
                await target.answer_photo(image_url, caption=content_service.SALAWAT_TEXT)
                return True

        has_media = await deliver_devotional_media(
            session, target, slug=slug, asset=asset, platform=platform, lang=lang,
        )
        if not has_media and not sent and asset.text_body:
            for chunk in asset.text_body.split("\x1e"):
                await target.answer(chunk)
            sent = True
        return sent or has_media
    except Exception:
        logger.warning(
            "Failed to deliver devotional content to %s:%s", platform_value, chat_id,
            exc_info=True,
        )
        return False
