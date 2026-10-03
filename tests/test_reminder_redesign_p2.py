"""Regressions for the first authorized reminder-redesign implementation step."""

from contextlib import asynccontextmanager
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from aiogram.types import URLInputFile

from khatmsaz.bot.handlers import create_khatm, join_flow, settings_menu
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.bot_registry.models import BotRole
from khatmsaz.modules.notification import service as notifications
from khatmsaz.modules.participation import service as participations
from khatmsaz.modules.participation import repository as participation_repo
from khatmsaz.modules.participation.commitment import is_regular_due


class State:
    def __init__(self, **data):
        self.data = data

    async def get_data(self):
        return self.data.copy()

    async def update_data(self, **data):
        self.data.update(data)

    async def clear(self):
        self.data.clear()


@asynccontextmanager
async def fake_scope():
    yield object()


@pytest.mark.asyncio
@pytest.mark.parametrize("registered", [True, False])
@pytest.mark.parametrize("role", [BotRole.MEMBER, BotRole.CREATOR])
async def test_accept_removes_only_consent_after_join_or_registration(monkeypatch, registered, role):
    from khatmsaz.bot.handlers import member_registration, registration

    events = []

    async def next_step(*args, **kwargs):
        assert kwargs["consent_accepted"] is True
        events.append("next")

    async def delete():
        events.append("delete-consent")

    monkeypatch.setattr(join_flow, "session_scope", fake_scope)
    monkeypatch.setattr(join_flow.identity_service, "resolve_or_provision_user", AsyncMock(
        return_value=SimpleNamespace(id=uuid4(), display_name="عضو"),
    ))
    monkeypatch.setattr(join_flow.settings_service, "is_registered", AsyncMock(return_value=registered))
    monkeypatch.setattr(join_flow, "resume_join_after_registration", next_step)
    monkeypatch.setattr(member_registration, "start_member_registration", next_step)
    monkeypatch.setattr(registration, "start_registration", next_step)
    message = SimpleNamespace(
        bot=SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM, khatmsaz_role=role),
        edit_reply_markup=AsyncMock(), delete=delete,
    )
    callback = SimpleNamespace(
        data="commitment_consent:accept:invitation", message=message,
        from_user=SimpleNamespace(id=123), answer=AsyncMock(),
    )
    await join_flow.accept_commitment(callback, State())
    assert events == ["next", "delete-consent"]


@pytest.mark.asyncio
async def test_consent_delete_failure_does_not_fail_join(monkeypatch):
    monkeypatch.setattr(join_flow, "session_scope", fake_scope)
    monkeypatch.setattr(join_flow.identity_service, "resolve_or_provision_user", AsyncMock(
        return_value=SimpleNamespace(id=uuid4(), display_name="عضو"),
    ))
    monkeypatch.setattr(join_flow.settings_service, "is_registered", AsyncMock(return_value=True))
    resume = AsyncMock()
    monkeypatch.setattr(join_flow, "resume_join_after_registration", resume)
    message = SimpleNamespace(
        bot=SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM),
        edit_reply_markup=AsyncMock(), delete=AsyncMock(side_effect=RuntimeError("cannot delete")),
    )
    await join_flow.accept_commitment(SimpleNamespace(
        data="commitment_consent:accept:invitation", message=message,
        from_user=SimpleNamespace(id=123), answer=AsyncMock(),
    ), State())
    resume.assert_awaited_once()
    message.edit_reply_markup.assert_awaited_once_with(reply_markup=None)


@pytest.mark.asyncio
async def test_failed_join_does_not_remove_consent_card(monkeypatch):
    monkeypatch.setattr(join_flow, "session_scope", fake_scope)
    monkeypatch.setattr(join_flow.identity_service, "resolve_or_provision_user", AsyncMock(
        return_value=SimpleNamespace(id=uuid4(), display_name="عضو"),
    ))
    monkeypatch.setattr(join_flow.settings_service, "is_registered", AsyncMock(return_value=True))
    monkeypatch.setattr(join_flow, "resume_join_after_registration", AsyncMock(side_effect=RuntimeError("db")))
    message = SimpleNamespace(
        bot=SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM),
        edit_reply_markup=AsyncMock(), delete=AsyncMock(),
    )
    with pytest.raises(RuntimeError):
        await join_flow.accept_commitment(SimpleNamespace(
            data="commitment_consent:accept:invitation", message=message,
            from_user=SimpleNamespace(id=123), answer=AsyncMock(),
        ), State())
    message.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_intro_reloads_same_url_bytes_without_changing_signed_url(monkeypatch):
    from khatmsaz.modules.bot_registry import service as registry

    url = "https://assets.example/intro.jpg?signature=unchanged"
    lookup = AsyncMock(return_value=url)
    monkeypatch.setattr(registry, "get_intro_image_for_category", lookup)
    monkeypatch.setattr(create_khatm, "session_scope", fake_scope)
    payloads = []
    current_bytes = b"old-image"

    async def stream_content(**kwargs):
        assert kwargs["url"] == url
        assert kwargs["headers"]["Cache-Control"] == "no-cache"
        yield current_bytes

    bot = SimpleNamespace(
        khatmsaz_platform=Platform.BALE,
        session=SimpleNamespace(stream_content=stream_content),
    )

    async def answer_photo(photo, **kwargs):
        assert isinstance(photo, URLInputFile)
        payloads.append(b"".join([chunk async for chunk in photo.read(bot)]))
        return SimpleNamespace(message_id=len(payloads))

    message = SimpleNamespace(bot=bot, answer_photo=answer_photo, answer=AsyncMock())
    state = State(lang="fa", template_type="SALAWAT", category_group=None)
    await create_khatm._show_intro_image(message, state)
    current_bytes = b"new-image"
    await create_khatm._show_intro_image(message, state)
    assert payloads == [b"old-image", b"new-image"]
    assert lookup.call_args.kwargs == {"platform": "BALE", "language": "fa"}
    assert state.data["_intro_mid"] == 2
    message.answer.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("ref,fail", [("file-id", False), ("https://assets.example/intro.jpg", True)])
async def test_intro_preserves_file_ids_and_text_fallback(monkeypatch, ref, fail):
    from khatmsaz.modules.bot_registry import service as registry

    monkeypatch.setattr(registry, "get_intro_image_for_category", AsyncMock(return_value=ref))
    monkeypatch.setattr(create_khatm, "session_scope", fake_scope)
    message = SimpleNamespace(
        bot=SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM),
        answer_photo=AsyncMock(return_value=SimpleNamespace(message_id=10)),
        answer=AsyncMock(return_value=SimpleNamespace(message_id=20)),
    )
    if fail:
        message.answer_photo.side_effect = RuntimeError("download unavailable")
    state = State(lang="fa", template_type="SALAWAT")
    await create_khatm._show_intro_image(message, state)
    assert state.data["_intro_mid"] == (20 if fail else 10)
    if not fail:
        assert message.answer_photo.call_args.args[0] == ref
        message.answer.assert_not_awaited()


@pytest.mark.asyncio
async def test_settings_clock_updates_regular_execution_without_changing_plan(monkeypatch):
    pid = uuid4()
    participation = SimpleNamespace(
        id=pid, commitment_mode="REGULAR", schedule_hour=9, schedule_anchor=0,
        schedule_freq="WEEKLY", schedule_weekdays="0,2,6", commitment_per_occurrence=3,
        schedule_last_sent_at=None,
    )
    preference = SimpleNamespace(reminder_hour=9, reminder_minute=0, enabled=True)

    async def upsert(session, participation_id, **values):
        assert participation_id == pid
        preference.__dict__.update(values)
        return preference

    session = SimpleNamespace(get=AsyncMock(return_value=participation), flush=AsyncMock())

    @asynccontextmanager
    async def scope():
        yield session

    monkeypatch.setattr(notifications.repository, "upsert_preference", upsert)
    monkeypatch.setattr(settings_menu, "session_scope", scope)
    monkeypatch.setattr(settings_menu, "_owned_reminder_context", AsyncMock(return_value=(
        SimpleNamespace(language="fa"), participation, SimpleNamespace(title="ختم تست"),
    )))
    await settings_menu.set_reminder(SimpleNamespace(
        data=f"set_reminder:{pid}:16:35", answer=AsyncMock(),
        message=SimpleNamespace(edit_text=AsyncMock()),
    ))
    assert await notifications.get_reminder_time(session, participation) == (16, 35)
    assert (preference.reminder_hour, preference.reminder_minute) == (16, 35)
    assert (participation.schedule_freq, participation.schedule_weekdays, participation.commitment_per_occurrence) == (
        "WEEKLY", "0,2,6", 3,
    )
    assert participation.schedule_last_sent_at is None
    for minute, expected in [(34, False), (35, True)]:
        assert is_regular_due(
            datetime(2026, 10, 3, 16, minute, tzinfo=ZoneInfo("Asia/Tehran")),
            participation.schedule_freq, participation.schedule_hour, participation.schedule_anchor,
            None, participation.schedule_weekdays,
        ) is expected


@pytest.mark.asyncio
async def test_count_settings_do_not_turn_into_regular_plan():
    participation = SimpleNamespace(commitment_mode="COUNT", schedule_hour=None, schedule_anchor=None)
    session = SimpleNamespace(get=AsyncMock(return_value=participation), flush=AsyncMock())
    await participation_repo.update_regular_reminder_time(session, uuid4(), hour=16, minute=35)
    assert participation.schedule_hour is None
    assert participation.schedule_anchor is None
    session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_regular_setup_keeps_preference_in_same_transaction(monkeypatch):
    set_plan = AsyncMock()
    set_clock = AsyncMock()
    monkeypatch.setattr(participation_repo, "set_commitment_schedule", set_plan)
    monkeypatch.setattr(notifications, "set_reminder_preference", set_clock)
    session, pid = object(), uuid4()
    await participations.set_commitment_schedule(
        session, pid, freq="DAILY", hour=6, minute=25, times_per_period=2,
    )
    set_plan.assert_awaited_once()
    set_clock.assert_awaited_once_with(session, pid, reminder_hour=6, reminder_minute=25)


@pytest.mark.asyncio
async def test_nonregular_clock_uses_worker_default_not_account_default(monkeypatch):
    monkeypatch.setattr(notifications.repository, "get_preference", AsyncMock(return_value=None))
    monkeypatch.setattr("khatmsaz.modules.system_settings.service.get_int", AsyncMock(return_value=11))
    assert await notifications.get_reminder_time(object(), SimpleNamespace(id=uuid4())) == (11, 0)
