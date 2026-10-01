from types import SimpleNamespace

import pytest
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import SendDocument
from aiogram.types import BufferedInputFile

from khatmsaz.bot.handlers import devotional
from khatmsaz.modules.identity.models import Platform


class _Message:
    def __init__(self):
        self.bot = object()
        self.calls = []

    async def answer_photo(self, value, **kwargs):
        self.calls.append(("IMAGE", value))

    async def answer_document(self, value, **kwargs):
        self.calls.append(("PDF", value))

    async def answer_audio(self, value, **kwargs):
        self.calls.append(("AUDIO", value))

    async def answer(self, value, **kwargs):
        self.calls.append(("TEXT", value))


@pytest.mark.asyncio
async def test_reading_media_is_delivered_image_first_then_pdf(monkeypatch):
    async def images(*args, **kwargs):
        return [SimpleNamespace(asset_ref="image-ref", page_number=1)]

    async def pdf(*args, **kwargs):
        return SimpleNamespace(asset_ref="pdf-ref")

    async def audios(*args, **kwargs):
        return []

    monkeypatch.setattr(devotional.content_service, "list_devotional_image_pages", images)
    monkeypatch.setattr(devotional.content_service, "get_devotional_pdf", pdf)
    monkeypatch.setattr(devotional.content_service, "list_devotional_audio_variants", audios)
    message = _Message()
    asset = SimpleNamespace(image_ref=None, image_platform=None, audio_ref=None, audio_platform=None)

    delivered = await devotional.deliver_devotional_media(
        object(), message, slug="dua-ahd", asset=asset,
        platform=Platform.TELEGRAM, lang="fa",
    )

    assert delivered is True
    assert [kind for kind, _ in message.calls] == ["IMAGE", "PDF"]


@pytest.mark.asyncio
async def test_member_bot_reuploads_creator_bot_file_id(monkeypatch):
    member_bot = object()
    sent = []

    class Message:
        bot = member_bot

        async def answer_document(self, value, **kwargs):
            sent.append(value)
            if isinstance(value, str):
                raise TelegramBadRequest(
                    method=SendDocument(chat_id=1, document=value),
                    message="Bad Request: wrong file identifier/HTTP URL specified",
                )

    class CreatorBot:
        async def download(self, ref, destination):
            assert ref == "creator-file-id"
            destination.write(b"pdf bytes")

    registry = SimpleNamespace(
        get_creator_bot=lambda platform: CreatorBot(),
    )
    monkeypatch.setattr(devotional, "get_registry", lambda: registry)

    await devotional._send_portable_media(
        Message(), kind="PDF", asset_ref="creator-file-id",
        platform=Platform.TELEGRAM, filename="dua-ahd.pdf",
    )

    assert isinstance(sent[-1], BufferedInputFile)
    assert sent[-1].filename == "dua-ahd.pdf"
