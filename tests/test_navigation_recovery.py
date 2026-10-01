from contextlib import asynccontextmanager
from types import SimpleNamespace

import pytest

from khatmsaz.bot.handlers import start
from khatmsaz.bot.keyboards import bail_if_menu_button
from khatmsaz.bot import navigation
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.khatm.models import KhatmTemplateType


class FakeState:
    def __init__(self):
        self.events = []

    async def clear(self):
        self.events.append("clear")

    async def update_data(self, **values):
        self.events.append(("update", values))


class FakeMessage:
    def __init__(self, text=""):
        self.text = text
        self.chat = SimpleNamespace(id=123)
        self.bot = SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM)
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))

    async def edit_reply_markup(self, **kwargs):
        return None


@pytest.mark.asyncio
@pytest.mark.parametrize("role", [UserRole.USER, UserRole.CREATOR, UserRole.SUPER_ADMIN])
async def test_global_cancel_clears_state_and_returns_role_aware_menu(monkeypatch, role):
    message = FakeMessage("/cancel")
    state = FakeState()
    expected = navigation.home_markup_for_role("fa", role)

    async def fake_home(_message, lang=None):
        return "fa", role, expected

    monkeypatch.setattr(start, "resolve_home_navigation", fake_home)
    await start.cancel_current_flow(message, state)

    assert state.events == ["clear"]
    assert message.answers[-1][1]["reply_markup"] == expected


@pytest.mark.asyncio
async def test_plain_start_clears_an_abandoned_state(monkeypatch):
    from khatmsaz.bot.handlers import create_khatm
    user = SimpleNamespace(id="user-id", role=UserRole.USER)
    wizard_started = []

    @asynccontextmanager
    async def fake_scope():
        yield object()

    async def fake_user(*args, **kwargs):
        return user

    async def fake_settings(*args, **kwargs):
        return SimpleNamespace(language_prompted=True, language="fa")

    async def fake_start_wizard(message, state):
        wizard_started.append((message, state))

    monkeypatch.setattr(start, "session_scope", fake_scope)
    monkeypatch.setattr(start.identity_service, "resolve_or_provision_user", fake_user)
    monkeypatch.setattr(start.settings_service, "get_or_create", fake_settings)
    monkeypatch.setattr(create_khatm, "start_wizard", fake_start_wizard)

    state = FakeState()
    message = FakeMessage("/start")
    await start.handle_start(message, state)

    assert state.events == ["clear"]
    assert message.answers[-1][1]["reply_markup"] == navigation.home_markup_for_role("fa", UserRole.USER)
    # Owner (2026-10-01): /start shows the welcome then goes STRAIGHT into the
    # create-khatm wizard again (new members get registration first via start_wizard).
    assert wizard_started == [(message, state)]


@pytest.mark.asyncio
async def test_first_language_choice_refreshes_creator_menu_and_starts_wizard(monkeypatch):
    from khatmsaz.bot.handlers import create_khatm

    user = SimpleNamespace(id="user-id", role=UserRole.USER)
    wizard_started = []

    @asynccontextmanager
    async def fake_scope():
        yield object()

    async def fake_user(*args, **kwargs):
        return user

    async def fake_set_language(*args, **kwargs):
        return None

    async def fake_start_wizard(message, state):
        wizard_started.append((message, state))

    monkeypatch.setattr(start, "session_scope", fake_scope)
    monkeypatch.setattr(start.identity_service, "resolve_or_provision_user", fake_user)
    monkeypatch.setattr(start.settings_service, "set_language", fake_set_language)
    monkeypatch.setattr(create_khatm, "start_wizard", fake_start_wizard)

    message = FakeMessage()
    callback = SimpleNamespace(
        data="first_lang:fa",
        message=message,
        from_user=SimpleNamespace(id=123),
    )

    async def answer(*args, **kwargs):
        return None

    callback.answer = answer
    state = FakeState()
    await start.choose_first_language(callback, state)

    assert message.answers[-1][1]["reply_markup"] == navigation.home_markup_for_role(
        "fa", UserRole.USER
    )
    assert wizard_started == [(message, state)]


@pytest.mark.asyncio
async def test_deep_link_clears_old_state_before_storing_new_join_context(monkeypatch):
    user = SimpleNamespace(id="user-id", role=UserRole.USER)
    khatm = SimpleNamespace(
        id="khatm-id", creator_user_id="creator-id",
        template_type=KhatmTemplateType.QURAN_PAGE,
        cover_status="NONE", cover_platform=None, cover_ref=None,
    )

    @asynccontextmanager
    async def fake_scope():
        yield object()

    async def fake_user(*args, **kwargs):
        return user

    async def fake_settings(*args, **kwargs):
        return SimpleNamespace(language="en")

    async def fake_khatm_id(*args, **kwargs):
        return "khatm-id"

    async def fake_khatm(*args, **kwargs):
        return khatm

    async def fake_creator(*args, **kwargs):
        return SimpleNamespace(display_name="Creator")

    async def fake_count(*args, **kwargs):
        return 0

    monkeypatch.setattr(start, "session_scope", fake_scope)
    monkeypatch.setattr(start.identity_service, "resolve_or_provision_user", fake_user)
    monkeypatch.setattr(start.identity_service, "find_by_id", fake_creator)
    monkeypatch.setattr(start.settings_service, "get_or_create", fake_settings)
    monkeypatch.setattr(start.invitation_service, "resolve_khatm_id", fake_khatm_id)
    monkeypatch.setattr(start.khatm_service, "get_khatm", fake_khatm)
    monkeypatch.setattr(start.participation_service, "count_for_khatm", fake_count)
    monkeypatch.setattr(start, "build_join_preview_message", lambda *args, **kwargs: "preview")

    state = FakeState()
    message = FakeMessage("/start join_fresh-token")
    command = SimpleNamespace(args="join_fresh-token")
    await start.handle_start_with_payload(message, command, state)

    assert state.events == ["clear", ("update", {"pending_join_token": "fresh-token"})]

    state.events.clear()
    await start.handle_start_with_payload(message, SimpleNamespace(args="unknown_payload"), state)
    assert state.events == ["clear"]
    assert message.answers[-1][0].startswith("Welcome")


@pytest.mark.asyncio
async def test_slash_command_is_never_accepted_as_free_text(monkeypatch):
    message = FakeMessage("/wallet")
    state = FakeState()
    expected = navigation.home_markup_for_role("fa", UserRole.CREATOR)

    async def fake_home(_message, lang=None):
        return "fa", UserRole.CREATOR, expected

    monkeypatch.setattr(navigation, "resolve_home_navigation", fake_home)
    assert await bail_if_menu_button(message, state) is True
    assert state.events == ["clear"]
    assert message.answers[-1][1]["reply_markup"] == expected


@pytest.mark.asyncio
async def test_join_preview_cancel_always_acknowledges_callback(monkeypatch):
    user = SimpleNamespace(id="user-id", role=UserRole.SUPER_ADMIN)

    @asynccontextmanager
    async def fake_scope():
        yield object()

    async def fake_user(*args, **kwargs):
        return user

    async def fake_settings(*args, **kwargs):
        return SimpleNamespace(language="fa")

    monkeypatch.setattr(start, "session_scope", fake_scope)
    monkeypatch.setattr(start.identity_service, "resolve_or_provision_user", fake_user)
    monkeypatch.setattr(start.settings_service, "get_or_create", fake_settings)

    message = FakeMessage()
    callback = SimpleNamespace(
        data="join_preview:cancel", message=message, from_user=SimpleNamespace(id=123),
        answered=False,
    )

    async def answer(*args, **kwargs):
        callback.answered = True

    callback.answer = answer
    state = FakeState()
    await start.accept_join_preview(callback, state)

    assert callback.answered is True
    assert state.events == ["clear"]
    assert message.answers[-1][1]["reply_markup"] == navigation.home_markup_for_role("fa", UserRole.SUPER_ADMIN)
