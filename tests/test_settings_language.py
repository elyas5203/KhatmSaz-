import pytest

from khatmsaz.modules.settings import service
from khatmsaz.modules.settings.models import FontSize


@pytest.mark.asyncio
async def test_set_language_validates_and_normalizes(monkeypatch):
    settings = type("Settings", (), {"language": "fa"})()

    class FakeSession:
        async def flush(self):
            return None

    async def fake_get_or_create(session, user_id):
        return settings

    monkeypatch.setattr(service, "get_or_create", fake_get_or_create)

    result = await service.set_language(FakeSession(), object(), " EN ")
    assert result.language == "en"

    with pytest.raises(ValueError):
        await service.set_language(FakeSession(), object(), "de")


@pytest.mark.asyncio
async def test_set_font_size_validates_and_persists(monkeypatch):
    settings = type("Settings", (), {"font_size": FontSize.NORMAL})()

    class FakeSession:
        async def flush(self):
            return None

    async def fake_get_or_create(session, user_id):
        return settings

    monkeypatch.setattr(service, "get_or_create", fake_get_or_create)
    result = await service.set_font_size(FakeSession(), object(), "large")
    assert result.font_size == FontSize.LARGE
    with pytest.raises(ValueError):
        await service.set_font_size(FakeSession(), object(), "huge")
