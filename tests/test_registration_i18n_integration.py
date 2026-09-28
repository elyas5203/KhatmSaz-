"""Registration language selection is loaded from real PostgreSQL."""

from types import SimpleNamespace

import pytest
from sqlalchemy import delete

from khatmsaz.bot.handlers.registration import (
    Registration,
    _gender_keyboard,
    _phone_keyboard,
    _province_keyboard,
    start_registration,
)
from khatmsaz.bot.handlers.profile import (
    ProfileEdit,
    _gender_keyboard as profile_gender_keyboard,
    _province_keyboard as profile_province_keyboard,
    begin_profile,
)
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.settings.models import UserSettings


class FakeState:
    def __init__(self):
        self.data = {}
        self.state = None

    async def update_data(self, **values):
        self.data.update(values)

    async def set_state(self, value):
        self.state = value

    async def clear(self):
        self.data = {}
        self.state = None


class FakeMessage:
    def __init__(self, chat_id: int):
        self.chat = SimpleNamespace(id=chat_id)
        self.bot = SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM)
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize("lang", ["ar", "en"])
async def test_registration_starts_in_the_users_saved_language(lang):
    chat_id = 9_700_000_000 + (1 if lang == "ar" else 2)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, Platform.TELEGRAM, chat_id)
        await settings_service.set_language(session, user.id, lang)
        user_id = user.id

    state = FakeState()
    message = FakeMessage(chat_id)
    await start_registration(message, state, pending_join_token="integration-token")

    assert state.state == Registration.entering_name
    assert state.data == {"pending_join_token": "integration-token", "language": lang}
    assert message.answers[0][0] == t("registration.ask_name", lang)
    assert _phone_keyboard(lang).keyboard[0][0].text == t("registration.share_phone", lang)
    assert _province_keyboard(lang).inline_keyboard[-1][0].text == t("registration.outside_iran", lang)
    assert _province_keyboard(lang).inline_keyboard[0][0].text == (
        "أذربيجان الشرقية" if lang == "ar" else "East Azerbaijan"
    )
    assert max(len(row) for row in _province_keyboard(lang).inline_keyboard) == 2
    genders = _gender_keyboard(lang).inline_keyboard[0]
    assert [item.text for item in genders] == [
        t("registration.gender_male", lang),
        t("registration.gender_female", lang),
    ]

    profile_state = FakeState()
    profile_message = FakeMessage(chat_id)
    await begin_profile(profile_message, profile_state)
    assert profile_state.state == ProfileEdit.entering_name
    assert profile_state.data == {"language": lang}
    assert profile_message.answers[0][0] == t("profile.ask_name", lang)
    assert profile_province_keyboard(lang).inline_keyboard[0][0].text == (
        "أذربيجان الشرقية" if lang == "ar" else "East Azerbaijan"
    )
    assert max(len(row) for row in profile_province_keyboard(lang).inline_keyboard) == 2
    assert [item.text for item in profile_gender_keyboard(lang).inline_keyboard[0]] == [
        t("registration.gender_male", lang),
        t("registration.gender_female", lang),
    ]

    async with session_scope() as session:
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
