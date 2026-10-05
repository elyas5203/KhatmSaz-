from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from khatmsaz.bot.handlers import portions
from khatmsaz.i18n import t
from khatmsaz.modules.khatm.models import KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.reminder_engine import service as reminders


@asynccontextmanager
async def scope():
    yield object()


@pytest.mark.asyncio
@pytest.mark.parametrize("pages", [None, 5])
async def test_quran_picker_always_receives_page_family(monkeypatch, pages):
    from khatmsaz.bot.handlers import member_commitment
    khatm = SimpleNamespace(id="k", template_type=KhatmTemplateType.QURAN_PAGE,
                            khatm_type=KhatmTypeEnum.OPEN, content_category_id=None)
    part = SimpleNamespace(id="p", is_committed=False, open_reading_pages_per_day=pages,
                           commitment_mode=None)
    monkeypatch.setattr(portions, "session_scope", scope)
    monkeypatch.setattr(portions, "_lang_for", AsyncMock(return_value="fa"))
    monkeypatch.setattr(portions.khatm_service, "get_khatm", AsyncMock(return_value=khatm))
    monkeypatch.setattr(portions.identity_service, "resolve_or_provision_user", AsyncMock(return_value=SimpleNamespace(id="u")))
    monkeypatch.setattr(portions, "_active_participation_for_current_bot", AsyncMock(return_value=part))
    setup = AsyncMock()
    picker = AsyncMock()
    monkeypatch.setattr(portions, "start_open_quran_setup", setup)
    monkeypatch.setattr(member_commitment, "start_commitment_mode_picker", picker)
    monkeypatch.setattr(portions, "safe_answer_callback", AsyncMock())
    bot = SimpleNamespace()
    message = SimpleNamespace(bot=bot, chat=SimpleNamespace(id=1), answer=AsyncMock())
    callback = SimpleNamespace(data="contribute:k", message=message, bot=bot, from_user=SimpleNamespace(id=1))
    state = SimpleNamespace(set_state=AsyncMock(), update_data=AsyncMock())
    await portions.ask_contribution_amount(callback, state)
    picker.assert_awaited_once()
    assert picker.await_args.kwargs["family"] == "QURAN"
    setup.assert_not_awaited()


@pytest.mark.asyncio
async def test_stored_quran_regular_never_uses_devotional_delivery(monkeypatch):
    part = SimpleNamespace(khatm_id="k")
    khatm = SimpleNamespace(template_type=KhatmTemplateType.QURAN_PAGE)
    monkeypatch.setattr(reminders.participation_service, "list_active_with_regular_schedule", AsyncMock(return_value=[part]))
    monkeypatch.setattr(reminders.khatm_service, "get_khatm", AsyncMock(return_value=khatm))
    monkeypatch.setattr(reminders.khatm_service, "has_started", lambda k: True)
    from khatmsaz.bot import notify_adapter
    send = AsyncMock()
    monkeypatch.setattr(notify_adapter, "send_devotional_content", send)
    assert await reminders.deliver_due_regular_commitments(object(), AsyncMock()) == 0
    send.assert_not_awaited()


@pytest.mark.parametrize("day", ["saturday", "sunday", "monday", "tuesday", "wednesday", "thursday", "friday"])
@pytest.mark.parametrize("lang", ["fa", "ar"])
def test_weekdays_have_readable_translations(day, lang):
    text = t(f"days.{day}", lang)
    assert text and "?" not in text and not text.startswith("days.")


@pytest.mark.asyncio
async def test_stale_quran_repetition_wizard_redirects_without_saving(monkeypatch):
    from khatmsaz.bot.handlers import member_commitment as handler
    monkeypatch.setattr(handler, "session_scope", scope)
    monkeypatch.setattr(handler, "_lang_of", lambda message: "fa")
    monkeypatch.setattr(handler.participation_service, "get_by_id", AsyncMock(return_value=SimpleNamespace(khatm_id="k", user_id="u", joined_via_bot_instance_id="b")))
    monkeypatch.setattr(handler.identity_service, "resolve_or_provision_user", AsyncMock(return_value=SimpleNamespace(id="u")))
    monkeypatch.setattr(handler.khatm_service, "get_khatm", AsyncMock(return_value=SimpleNamespace(id="k", template_type=KhatmTemplateType.QURAN_PAGE)))
    save = AsyncMock()
    setup = AsyncMock()
    monkeypatch.setattr(handler.participation_service, "set_commitment_schedule", save)
    monkeypatch.setattr(portions, "start_open_quran_setup", setup)
    state = SimpleNamespace(get_data=AsyncMock(return_value={"commit_pid": "p", "commit_freq": "DAILY", "commit_times": 3}), clear=AsyncMock())
    message = SimpleNamespace(bot=SimpleNamespace(khatmsaz_role="MEMBER", khatmsaz_instance_id="b"), chat=SimpleNamespace(id=1))
    await handler._save_regular(message, state, 17, 32)
    save.assert_not_awaited()
    setup.assert_awaited_once_with(message, state, khatm_id="k", lang="fa")


@pytest.mark.asyncio
async def test_regular_contribution_button_opens_exact_share_instead_of_bare_amount(monkeypatch):
    from khatmsaz.modules.share_occurrence import repository as shares
    khatm = SimpleNamespace(id="k", template_type="QURAN_PAGE", commitment_policy="MEMBER_CHOICE")
    part = SimpleNamespace(id="p", commitment_mode="REGULAR")
    monkeypatch.setattr(portions, "session_scope", scope)
    monkeypatch.setattr(portions, "_lang_for", AsyncMock(return_value="fa"))
    monkeypatch.setattr(portions.khatm_service, "get_khatm", AsyncMock(return_value=khatm))
    monkeypatch.setattr(portions.identity_service, "resolve_or_provision_user", AsyncMock(return_value=SimpleNamespace(id="u")))
    monkeypatch.setattr(portions, "_active_participation_for_current_bot", AsyncMock(return_value=part))
    monkeypatch.setattr(shares, "list_outstanding", AsyncMock(return_value=[]))
    monkeypatch.setattr(shares, "has_any", AsyncMock(return_value=True))
    monkeypatch.setattr(portions, "safe_answer_callback", AsyncMock())
    bot = SimpleNamespace()
    message = SimpleNamespace(bot=bot, chat=SimpleNamespace(id=1), answer=AsyncMock())
    state = SimpleNamespace(set_state=AsyncMock())
    await portions.ask_contribution_amount(SimpleNamespace(data="contribute:k", bot=bot, message=message, from_user=SimpleNamespace(id=1)), state)
    state.set_state.assert_not_awaited()
    assert message.answer.await_args.kwargs["reply_markup"].inline_keyboard[0][0].callback_data == "today_pick:p"
