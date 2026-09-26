"""Telegram Bot instance factory."""

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from khatmsaz.config import get_settings
from khatmsaz.modules.identity.models import Platform


def build_telegram_bot(token: str | None = None) -> Bot:
    settings = get_settings()
    session = AiohttpSession(proxy=settings.bot_http_proxy_url or None)
    bot = Bot(
        token=token or settings.telegram_bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    bot.khatmsaz_platform = Platform.TELEGRAM  # type: ignore[attr-defined]
    return bot
