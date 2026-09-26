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
        
        if bot_instance_id:
            bot = registry.get_by_instance_id(bot_instance_id)
        else:
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
            bot = registry.get_by_instance_id(bot_instance_id)
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
) -> None:
    from khatmsaz.core.bot_registry import get_registry
    registry = get_registry()
    if bot_instance_id:
        bot = registry.get_by_instance_id(bot_instance_id)
    else:
        bot = registry.get_creator_bot(Platform(platform_value))
    if bot is None:
        return
    try:
        await bot.send_message(chat_id=int(chat_id), text=text, reply_markup=reply_markup)
    except Exception:
        logger.warning(
            "Failed to deliver keyboard message to %s:%s", platform_value, chat_id, exc_info=True
        )
