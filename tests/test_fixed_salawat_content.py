from types import SimpleNamespace

import pytest

from khatmsaz.bot.handlers.portions import _send_recitation_content
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.khatm.models import KhatmTemplateType
from khatmsaz.web.app import app


class FakeMessage:
    def __init__(self):
        self.answers = []
        self.photos = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))

    async def answer_photo(self, photo, **kwargs):
        self.photos.append((photo, kwargs))


def _plain_salawat():
    return SimpleNamespace(
        template_type=KhatmTemplateType.SALAWAT,
        description=None,
        content_category_id=None,
    )


@pytest.mark.asyncio
async def test_plain_salawat_sends_exact_owner_text_without_category(monkeypatch):
    async def no_asset(session, slug):
        return None

    monkeypatch.setattr(content_service, "get_devotional_asset", no_asset)
    message = FakeMessage()
    await _send_recitation_content(object(), message, _plain_salawat())

    assert message.answers == [(content_service.SALAWAT_TEXT, {})]
    assert message.photos == []


@pytest.mark.asyncio
async def test_plain_salawat_uses_panel_image_with_fixed_text_caption(monkeypatch):
    async def image_asset(session, slug):
        return SimpleNamespace(image_ref="https://cdn.example.test/salawat.jpg")

    monkeypatch.setattr(content_service, "get_devotional_asset", image_asset)
    message = FakeMessage()
    await _send_recitation_content(object(), message, _plain_salawat())

    assert message.answers == []
    assert message.photos == [(
        "https://cdn.example.test/salawat.jpg",
        {"caption": content_service.SALAWAT_TEXT},
    )]


@pytest.mark.asyncio
async def test_plain_salawat_resolves_server_filename(monkeypatch):
    async def image_asset(session, slug):
        return SimpleNamespace(image_ref="salawat.jpg")

    monkeypatch.setattr(content_service, "get_devotional_asset", image_asset)
    monkeypatch.setattr(
        "khatmsaz.bot.handlers.portions.get_settings",
        lambda: SimpleNamespace(
            admin_web_base_url="https://panel.example.test",
            public_web_base_url="",
        ),
    )
    message = FakeMessage()
    await _send_recitation_content(object(), message, _plain_salawat())

    assert message.answers == []
    assert message.photos == [(
        "https://panel.example.test/static/devotional-images/salawat.jpg",
        {"caption": content_service.SALAWAT_TEXT},
    )]


def test_admin_panel_exposes_fixed_salawat_image_endpoint():
    routes = {(route.path, method) for route in app.routes for method in getattr(route, "methods", set())}
    assert ("/devotionals/salawat/image", "POST") in routes
