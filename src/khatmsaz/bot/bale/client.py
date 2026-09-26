"""Bale Bot instance factory.

Bale's bot platform speaks a Telegram-compatible Bot API at a different base
URL (https://tapi.bale.ai by default). Reusing aiogram here — instead of a
second bot framework — is exactly what keeps Telegram and Bale as two thin
adapters over one shared domain/handler layer.
"""

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode

from khatmsaz.config import get_settings
from khatmsaz.modules.identity.models import Platform


def build_bale_bot(token: str | None = None) -> Bot:
    settings = get_settings()
    api_server = TelegramAPIServer.from_base(settings.bale_api_base_url)
    session = AiohttpSession(api=api_server, proxy=settings.bot_http_proxy_url or None)
    bot = Bot(
        token=token or settings.bale_bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    bot.khatmsaz_platform = Platform.BALE  # type: ignore[attr-defined]
    return bot
