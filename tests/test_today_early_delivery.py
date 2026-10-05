from contextlib import asynccontextmanager
from types import SimpleNamespace
import inspect

import pytest

from khatmsaz.bot.handlers import public_khatms, report, start
from khatmsaz.i18n import t
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.participation.commitment import CommitmentMode
from khatmsaz.modules.bot_registry.models import BotRole
from khatmsaz.modules.khatm.models import KhatmTemplateType


class FakeMessage:
    def __init__(self):
        self.bot = SimpleNamespace(
            khatmsaz_platform=Platform.TELEGRAM,
            khatmsaz_language="fa",
            khatmsaz_instance_id="bot-1",
            khatmsaz_role=BotRole.MEMBER,
        )
        self.chat = SimpleNamespace(id=100)
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))


class FakeCallback:
    def __init__(self, participation_id):
        self.data = f"today_pick:{participation_id}"
        self.from_user = SimpleNamespace(id=100)
        self.message = FakeMessage()
        self.answered = []

    async def answer(self, *args, **kwargs):
        self.answered.append((args, kwargs))


@pytest.mark.asyncio
async def test_today_lists_khatms_before_delivering_any_share(monkeypatch):
    participations = [
        SimpleNamespace(id="p1", khatm_id="k1"),
        SimpleNamespace(id="p2", khatm_id="k2"),
        SimpleNamespace(id="p3", khatm_id="k3"),
    ]
    khatms = {
        "k1": SimpleNamespace(title="ختم اول"),
        "k2": SimpleNamespace(title="ختم دوم"),
        "k3": SimpleNamespace(title="ختم سوم"),
    }

    @asynccontextmanager
    async def fake_scope():
        yield object()

    async def fake_user(*args, **kwargs):
        return SimpleNamespace(id="u1")

    async def fake_settings(*args, **kwargs):
        return SimpleNamespace(language="fa")

    async def fake_list(*args, **kwargs):
        return participations

    async def fake_khatm(_session, khatm_id):
        return khatms[khatm_id]

    monkeypatch.setattr(report, "session_scope", fake_scope)
    monkeypatch.setattr(report.identity_service, "resolve_or_provision_user", fake_user)
    monkeypatch.setattr(report.settings_service, "get_or_create", fake_settings)
    monkeypatch.setattr(report.participation_service, "list_my_active", fake_list)
    monkeypatch.setattr(report.khatm_service, "get_khatm", fake_khatm)
    monkeypatch.setattr(report.khatm_service, "has_started", lambda _k: True)

    message = FakeMessage()
    await report.today_overview(message)

    assert len(message.answers) == 1
    keyboard = message.answers[0][1]["reply_markup"]
    assert [row[0].text for row in keyboard.inline_keyboard] == [
        "🌱 ختم اول", "🌱 ختم دوم", "🌱 ختم سوم",
    ]
    assert [row[0].callback_data for row in keyboard.inline_keyboard] == [
        "today_pick:p1", "today_pick:p2", "today_pick:p3",
    ]


@pytest.mark.asyncio
async def test_early_regular_share_uses_same_occurrence_delivery_as_scheduler(monkeypatch):
    participation = SimpleNamespace(
        id="p1", user_id="u1", khatm_id="k1", joined_via_bot_instance_id="bot-1",
        commitment_mode=CommitmentMode.REGULAR.value, schedule_last_sent_at=None,
        commitment_per_occurrence=2, open_reading_pages_per_day=None,
    )
    khatm = SimpleNamespace(id="k1", title="دعای عهد", template_type="DUA")

    @asynccontextmanager
    async def fake_scope():
        yield object()

    async def fake_user(*args, **kwargs):
        return SimpleNamespace(id="u1")

    async def fake_participation(*args, **kwargs):
        return participation

    async def fake_khatm(*args, **kwargs):
        return khatm

    async def fake_settings(*args, **kwargs):
        return SimpleNamespace(timezone="Asia/Tehran")

    monkeypatch.setattr(report, "session_scope", fake_scope)
    monkeypatch.setattr(report.identity_service, "resolve_or_provision_user", fake_user)
    monkeypatch.setattr(report.participation_service, "get_by_id", fake_participation)
    monkeypatch.setattr(report.khatm_service, "get_khatm", fake_khatm)
    monkeypatch.setattr(report.khatm_service, "has_started", lambda _k: True)
    monkeypatch.setattr(report.settings_service, "get_or_create", fake_settings)
    # L5 (owner 2026-09-30): the zekr content is delivered before the done button;
    # stub it so this unit test stays DB-free.
    import khatmsaz.bot.handlers.portions as _portions
    async def _no_content(*a, **k):
        return True
    monkeypatch.setattr(_portions, "_send_recitation_content", _no_content)
    from unittest.mock import AsyncMock
    from khatmsaz.modules.share_occurrence import delivery, repository
    occurrence = SimpleNamespace(id="share-1", delivered_at=None)
    prepare, send = AsyncMock(return_value=occurrence), AsyncMock(return_value=True)
    monkeypatch.setattr(delivery, "prepare", prepare)
    monkeypatch.setattr(delivery, "deliver", send)
    monkeypatch.setattr(repository, "list_outstanding", AsyncMock(return_value=[]))
    monkeypatch.setattr(repository, "list_legacy_portions", AsyncMock(return_value=[]))
    callback = FakeCallback("p1")
    await report.deliver_today_early(callback)

    assert prepare.await_args.kwargs["manual"] is True
    assert send.await_args.args[1] is occurrence


@pytest.mark.asyncio
async def test_open_devotional_today_sends_content_before_action(monkeypatch):
    participation = SimpleNamespace(
        id="p1", user_id="u1", khatm_id="k1", joined_via_bot_instance_id="bot-1",
        commitment_mode=None, open_reading_pages_per_day=None,
    )
    khatm = SimpleNamespace(id="k1", title="زیارت عاشورا", template_type=KhatmTemplateType.SALAWAT)

    @asynccontextmanager
    async def fake_scope():
        yield object()

    async def fake_user(*args, **kwargs): return SimpleNamespace(id="u1")
    async def fake_participation(*args, **kwargs): return participation
    async def fake_khatm(*args, **kwargs): return khatm
    async def fake_settings(*args, **kwargs): return SimpleNamespace(timezone="Asia/Tehran")
    async def fake_none(*args, **kwargs): return None
    async def fake_false(*args, **kwargs): return False
    async def fake_record(*args, **kwargs): return None

    monkeypatch.setattr(report, "session_scope", fake_scope)
    monkeypatch.setattr(report.identity_service, "resolve_or_provision_user", fake_user)
    monkeypatch.setattr(report.participation_service, "get_by_id", fake_participation)
    monkeypatch.setattr(report.khatm_service, "get_khatm", fake_khatm)
    monkeypatch.setattr(report.khatm_service, "has_started", lambda _k: True)
    monkeypatch.setattr(report.settings_service, "get_or_create", fake_settings)
    monkeypatch.setattr(report.allocation_service, "get_current_portion", fake_none)
    monkeypatch.setattr(report.notification_service, "already_sent_today", fake_false)
    monkeypatch.setattr(report.notification_service, "record_sent", fake_record)

    import khatmsaz.bot.handlers.portions as _portions
    async def fake_content(_session, message, _khatm):
        await message.answer("متن کامل زیارت")
        return True
    monkeypatch.setattr(_portions, "_send_recitation_content", fake_content)

    callback = FakeCallback("p1")
    await report.deliver_today_early(callback)

    assert callback.message.answers[0][0] == "متن کامل زیارت"
    assert callback.message.answers[-1][1]["reply_markup"].inline_keyboard[0][0].callback_data == "contribute:k1"


def test_every_public_join_routes_through_the_explicit_consent_gate():
    assert "if not consent_accepted" in inspect.getsource(start.resume_join_after_registration)
    assert "consent_accepted=False" in inspect.getsource(public_khatms.join_public_khatm)


def test_family_intro_copy_names_the_destination_bot():
    assert t("intro.image_caption.DUA_ZIYARAT", "fa") == (
        "مخاطبان شما وارد بات «ختم دعا و زیارت» می‌شوند.\n"
        "همهٔ ختم‌ها به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف برگزار می‌شوند 🌱"
    )
