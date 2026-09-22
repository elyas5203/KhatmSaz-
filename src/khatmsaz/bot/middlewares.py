"""Bot-wide moderation gate: a SUSPENDED/BANNED user gets a single friendly
message and nothing else runs for them — no handler needs to remember to
check this itself.
"""

from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from khatmsaz.core.db import session_scope
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform

_BLOCKED_TEXT = (
    "حساب شما توسط مدیریت مسدود شده و امکان استفاده از ربات رو ندارید. "
    "در صورت اعتراض با پشتیبانی تماس بگیرید."
)


class ModerationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        chat_id = _extract_chat_id(event)
        if chat_id is None:
            return await handler(event, data)

        bot = data.get("bot")
        platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)

        async with session_scope() as session:
            user = await identity_service.find_by_platform(session, platform, str(chat_id))
            if user is not None and await identity_service.is_blocked(user):
                await _reply_blocked(event)
                return None
            if user is not None:
                user.last_activity_at = datetime.now(timezone.utc)
                await session.flush()

        return await handler(event, data)


def _extract_chat_id(event: TelegramObject) -> int | None:
    message = getattr(event, "message", None) or event
    chat = getattr(message, "chat", None)
    if chat is not None:
        return chat.id
    from_user = getattr(event, "from_user", None)
    return from_user.id if from_user is not None else None


async def _reply_blocked(event: TelegramObject) -> None:
    message = getattr(event, "message", None)
    if message is not None:
        await message.answer(_BLOCKED_TEXT)
    elif hasattr(event, "answer"):
        await event.answer(_BLOCKED_TEXT, show_alert=True)
