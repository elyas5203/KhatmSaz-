from unittest.mock import AsyncMock

import pytest

from khatmsaz.modules.system_settings import service


@pytest.mark.asyncio
async def test_panel_logo_accepts_https_and_blank(monkeypatch):
    save = AsyncMock()
    monkeypatch.setattr(service.repository, "set", save)

    await service.set_str(None, "panel_logo_url", " https://cdn.example/logo.png ")
    save.assert_awaited_once_with(None, "panel_logo_url", "https://cdn.example/logo.png")

    save.reset_mock()
    await service.set_str(None, "panel_logo_url", "")
    save.assert_awaited_once_with(None, "panel_logo_url", "")


@pytest.mark.asyncio
@pytest.mark.parametrize("value", ["javascript:alert(1)", "//example.com/logo.png", "not-a-url"])
async def test_panel_logo_rejects_unsafe_or_relative_urls(monkeypatch, value):
    save = AsyncMock()
    monkeypatch.setattr(service.repository, "set", save)

    with pytest.raises(ValueError):
        await service.set_str(None, "panel_logo_url", value)
    save.assert_not_awaited()


@pytest.mark.asyncio
async def test_custom_khatm_phone_accepts_normalized_phone_and_rejects_text(monkeypatch):
    save = AsyncMock()
    monkeypatch.setattr(service.repository, "set", save)

    await service.set_str(None, "custom_khatm_admin_phone", " +98 (912) 123-4567 ")
    save.assert_awaited_once_with(None, "custom_khatm_admin_phone", "+989121234567")

    with pytest.raises(ValueError):
        await service.set_str(None, "custom_khatm_admin_phone", "admin username")
