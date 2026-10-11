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
from aiogram.methods import TelegramMethod
from aiogram.methods.base import TelegramType

from khatmsaz.bot.bale.formatting import html_to_bale_markdown
from khatmsaz.config import get_settings
from khatmsaz.modules.identity.models import Platform


class BaleAiohttpSession(AiohttpSession):
    """Session adapter for Bale Bot API.

    Transforms HTML formatted text and captions into Bale Markdown before
    payload serialization, preventing raw HTML tags from displaying in Bale.
    """

    async def make_request(
        self,
        bot: Bot,
        method: TelegramMethod[TelegramType],
        timeout: int | None = None,
    ) -> TelegramType:
        if hasattr(method, "text") and isinstance(method.text, str):
            method.text = html_to_bale_markdown(method.text)
        if hasattr(method, "caption") and isinstance(method.caption, str):
            method.caption = html_to_bale_markdown(method.caption)
        if hasattr(method, "parse_mode"):
            # Bale renders Markdown natively and rejects/misinterprets parse_mode=HTML
            method.parse_mode = None
        return await super().make_request(bot, method, timeout=timeout)


def build_bale_bot(token: str | None = None) -> Bot:
    settings = get_settings()
    api_server = TelegramAPIServer.from_base(settings.bale_api_base_url)
    session = BaleAiohttpSession(api=api_server, proxy=settings.bot_http_proxy_url or None)
    bot = Bot(
        token=token or settings.bale_bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=None),
    )
    bot.khatmsaz_platform = Platform.BALE  # type: ignore[attr-defined]
    return bot
