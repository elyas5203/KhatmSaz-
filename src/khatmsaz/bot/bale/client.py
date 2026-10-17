"""Bale Bot instance factory.

Bale's bot platform speaks a Telegram-compatible Bot API at a different base
URL (https://tapi.bale.ai by default). Reusing aiogram here — instead of a
second bot framework — is exactly what keeps Telegram and Bale as two thin
adapters over one shared domain/handler layer.
"""

from aiohttp import FormData
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.methods import TelegramMethod
from aiogram.methods.base import TelegramType
from aiogram.types import InputFile

from khatmsaz.bot.bale.formatting import html_to_bale_markdown
from khatmsaz.config import get_settings
from khatmsaz.modules.identity.models import Platform


class BaleAiohttpSession(AiohttpSession):
    """Session adapter for Bale Bot API.

    Transforms HTML formatted text and captions into Bale Markdown before
    payload serialization, preventing raw HTML tags from displaying in Bale.
    Also handles direct multipart file upload serialization for Bale's Bot API.
    """

    def build_form_data(self, bot: Bot, method: TelegramMethod[TelegramType]) -> FormData:
        form = FormData(quote_fields=False)
        dump = method.model_dump(warnings=False)
        for key, value in dump.items():
            if value is None:
                continue
            if isinstance(value, InputFile):
                content_type = None
                fname = getattr(value, "filename", "") or key
                lower_fname = fname.lower()
                if lower_fname.endswith((".jpg", ".jpeg")):
                    content_type = "image/jpeg"
                elif lower_fname.endswith(".png"):
                    content_type = "image/png"
                elif lower_fname.endswith(".mp3"):
                    content_type = "audio/mpeg"
                elif lower_fname.endswith(".ogg"):
                    content_type = "audio/ogg"
                elif lower_fname.endswith(".pdf"):
                    content_type = "application/pdf"
                elif lower_fname.endswith((".mp4", ".mkv", ".mov", ".avi")):
                    content_type = "video/mp4"
                form.add_field(
                    key,
                    value.read(bot),
                    filename=fname,
                    content_type=content_type,
                )
            else:
                prepared = self.prepare_value(value, bot=bot, files={})
                if prepared is not None:
                    form.add_field(key, prepared)
        return form

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
