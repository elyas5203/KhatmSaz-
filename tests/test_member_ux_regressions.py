from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from khatmsaz.bot.handlers import member_commitment
from khatmsaz.bot.handlers import create_khatm
from khatmsaz.bot.handlers.registration import _registration_prompt
from khatmsaz.bot import notify_adapter
from khatmsaz.bot.keyboards import member_menu_keyboard
from khatmsaz.i18n import t
from khatmsaz.modules.reminder_engine import service as reminder_service
from khatmsaz.modules.identity.models import Platform


class _State:
    def __init__(self, data=None):
        self.data = dict(data or {})

    async def get_data(self):
        return dict(self.data)

    async def update_data(self, **values):
        self.data.update(values)

    async def set_state(self, value):
        self.state = value


@pytest.mark.asyncio
async def test_creator_registration_replaces_previous_question_and_typed_answer():
    deleted = []

    class Bot:
        async def delete_message(self, chat_id, message_id):
            deleted.append((chat_id, message_id))

    class Message:
        message_id = 22
        chat = SimpleNamespace(id=7)
        from_user = SimpleNamespace(is_bot=False)
        bot = Bot()

        async def delete(self):
            deleted.append((7, 22))

        async def answer(self, text, **kwargs):
            return SimpleNamespace(message_id=33)

    state = _State({"_registration_mid": 11})
    await _registration_prompt(Message(), state, "next")

    assert (7, 22) in deleted
    assert (7, 11) in deleted
    assert state.data["_registration_mid"] == 33


def test_member_questions_are_visually_distinct_and_weekly_copy_is_unambiguous():
    question = member_commitment._question("عدد را بنویسید")
    weekly = t("commit.ask_times_per_period.dua", "fa", period=t("commit.period.these_days", "fa"))

    assert "❓ <b>سؤال این مرحله</b>" in question
    assert "هر هر" not in weekly
    assert "عدد را بنویسید" in weekly
    assert "تک‌تک آن روزها" in weekly


def test_member_menu_fits_in_four_logical_rows():
    keyboard = member_menu_keyboard("fa").keyboard
    assert len(keyboard) == 4
    assert len(keyboard[0]) == 1
    assert len(keyboard[1]) == 2
    assert len(keyboard[2]) == 2
    assert len(keyboard[3]) == 1


@pytest.mark.asyncio
async def test_creator_intro_image_is_deleted_when_continue_is_tapped():
    deleted = []

    class Bot:
        async def delete_message(self, chat_id, message_id):
            deleted.append((chat_id, message_id))

    class Message:
        message_id = 81
        chat = SimpleNamespace(id=7)
        from_user = SimpleNamespace(is_bot=True)
        bot = Bot()

        async def answer(self, text, **kwargs):
            return SimpleNamespace(message_id=82)

    class Callback:
        message = Message()

        async def answer(self, **kwargs):
            pass

    state = _State({
        "lang": "fa", "_intro_mid": 81, "template_type": "SALAWAT",
        "category_group": "DUA", "content_category_title": "زیارت عاشورا",
    })
    await create_khatm.intro_continue(Callback(), state)

    assert deleted == [(7, 81)]
    assert state.data["_intro_mid"] is None


@pytest.mark.asyncio
async def test_regular_reminder_sends_content_before_action_message(monkeypatch):
    events = []
    participation = SimpleNamespace(
        id="pid", khatm_id="kid", user_id="uid", schedule_freq="WEEKLY", commitment_mode="REGULAR",
        schedule_hour=13, schedule_anchor=36, schedule_last_sent_at=None,
        schedule_weekdays="3", commitment_per_occurrence=2,
        joined_via_bot_instance_id="bot-id",
    )
    khatm = SimpleNamespace(id="kid", title="زیارت عاشورا")
    settings = SimpleNamespace(timezone="Asia/Tehran", language="fa")
    identity = SimpleNamespace(platform=SimpleNamespace(value="TELEGRAM"), subject="123")

    async def _list(*args, **kwargs): return [participation]
    async def _khatm(*args, **kwargs): return khatm
    async def _settings(*args, **kwargs): return settings
    async def _identities(*args, **kwargs): return [identity]
    async def _content(*args, **kwargs): events.append("content"); return True
    async def _keyboard(*args, **kwargs): events.append("reminder"); return True
    async def _mark(*args, **kwargs): events.append("marked")

    monkeypatch.setattr(reminder_service.participation_service, "list_active_with_regular_schedule", _list)
    monkeypatch.setattr(reminder_service.khatm_service, "get_khatm", _khatm)
    monkeypatch.setattr(reminder_service.khatm_service, "has_started", lambda value: True)
    monkeypatch.setattr(reminder_service.settings_service, "get_or_create", _settings)
    monkeypatch.setattr(reminder_service.identity_service, "list_identities_for_user", _identities)
    monkeypatch.setattr(reminder_service, "_render_or_default", lambda *a, **k: _async_value("وقت خواندن"))
    monkeypatch.setattr(reminder_service, "_notify_user_with_keyboard", _keyboard)
    monkeypatch.setattr(reminder_service.participation_service, "mark_schedule_sent_now", _mark)
    monkeypatch.setattr("khatmsaz.bot.notify_adapter.send_devotional_content", _content)
    monkeypatch.setattr("khatmsaz.modules.participation.commitment.is_regular_due", lambda *a, **k: True)

    delivered = await reminder_service.deliver_due_regular_commitments(object(), lambda *a, **k: None)

    assert delivered == 1
    assert events == ["content", "reminder", "marked"]


async def _async_value(value):
    return value


@pytest.mark.asyncio
async def test_scheduled_devotional_content_prefers_registered_pdf(monkeypatch):
    sent = []

    class Bot:
        khatmsaz_platform = Platform.TELEGRAM

        async def send_document(self, chat_id, document, **kwargs):
            sent.append(("pdf", chat_id, document))

        async def send_message(self, chat_id, text, **kwargs):
            sent.append(("text", chat_id, text))

        async def send_photo(self, chat_id, photo, **kwargs):
            sent.append(("photo", chat_id, photo))

        async def send_audio(self, chat_id, audio, **kwargs):
            sent.append(("audio", chat_id, audio))

    bot = Bot()
    registry = SimpleNamespace(
        get_by_instance_id=lambda value: bot,
        get_creator_bot=lambda platform: bot,
    )
    category = SimpleNamespace(devotional_slug="ziyarat-ashura", image_url=None, body_text=None)
    asset = SimpleNamespace(
        image_ref=None, image_platform=None, audio_ref=None, audio_platform=None,
        text_body="متن طولانی",
    )

    async def _category(*args, **kwargs): return category
    async def _asset(*args, **kwargs): return asset
    async def _none_list(*args, **kwargs): return []
    async def _pdf(*args, **kwargs): return SimpleNamespace(asset_ref="pdf-file-id")

    monkeypatch.setattr("khatmsaz.core.bot_registry.get_registry", lambda: registry)
    monkeypatch.setattr("khatmsaz.modules.khatm_category.service.get", _category)
    monkeypatch.setattr(notify_adapter.content_service, "get_devotional_asset", _asset)
    monkeypatch.setattr(notify_adapter.content_service, "list_devotional_image_pages", _none_list)
    monkeypatch.setattr(notify_adapter.content_service, "get_devotional_pdf", _pdf)
    monkeypatch.setattr(notify_adapter.content_service, "list_devotional_audio_variants", _none_list)

    khatm = SimpleNamespace(description=None, content_category_id="cid")
    delivered = await notify_adapter.send_devotional_content(
        object(), "TELEGRAM", "123", khatm=khatm, lang="fa", bot_instance_id="bot-id",
    )

    assert delivered is True
    assert sent == [("pdf", 123, "pdf-file-id")]
