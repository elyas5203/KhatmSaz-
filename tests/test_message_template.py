from types import SimpleNamespace

import pytest

from khatmsaz.modules.message_template import repository, service


def test_validate_body_accepts_reminder_placeholders():
    service.validate_body("عنوان {{title}}، صفحات {{start}} تا {{end}}")


@pytest.mark.parametrize(
    "body",
    ["متن {{unknown}}", "متن {{title}", "متن {title}}"],
)
def test_validate_body_rejects_unknown_or_malformed_placeholders(body):
    with pytest.raises(ValueError):
        service.validate_body(body)


@pytest.mark.asyncio
async def test_render_replaces_known_placeholders_and_preserves_unknown(monkeypatch):
    async def fake_get_latest(session, key, locale):
        assert (key, locale) == ("reminder.first", "fa")
        return SimpleNamespace(body="سلام {{ name }}؛ {{missing}}")

    monkeypatch.setattr(repository, "get_latest", fake_get_latest)

    result = await service.render(object(), "reminder.first", name="کاربر")

    assert result == "سلام کاربر؛ {{missing}}"


@pytest.mark.asyncio
async def test_render_uses_fallback_locale(monkeypatch):
    calls = []

    async def fake_get_latest(session, key, locale):
        calls.append(locale)
        if locale == "fa":
            return SimpleNamespace(body="متن پیش‌فرض {{value}}")
        return None

    monkeypatch.setattr(repository, "get_latest", fake_get_latest)

    result = await service.render(object(), "key", locale="en", value=7)

    assert result == "متن پیش‌فرض 7"
    assert calls == ["en", "fa"]
