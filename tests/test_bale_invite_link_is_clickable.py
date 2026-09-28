"""Owner-reported bug (2026-09-22): "لینک جوین تو بله مشکل داره... این کد
رو براشون بفرستید تا داخل بله بفرستن: /start join_xxx ... خرابه." The
Bale invite instruction was raw text asking the recipient to manually
type a `/start join_<token>` command — error-prone and not a real link.
Fixed to build a real clickable `ble.ir` deep link, matching the format
`portions.py::_invite_friends_line` already uses elsewhere in this
codebase for Bale invites."""

from types import SimpleNamespace

import pytest
from sqlalchemy import delete

from khatmsaz.bot.handlers.create_khatm import _finish_creating_khatm
from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.core.bot_registry import BotRegistry, set_registry
from khatmsaz.modules.bot_registry.models import BotCategory, BotRole
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.khatm.models import Khatm, KhatmTemplateType, KhatmTypeEnum, KhatmVisibility


class FakeState:
    def __init__(self):
        self.data = {}

    async def clear(self):
        self.data = {}

    async def get_data(self):
        return dict(self.data)

    async def update_data(self, **values):
        self.data.update(values)


class FakeMessage:
    def __init__(self, chat_id, platform):
        self.chat = SimpleNamespace(id=chat_id)
        self.bot = SimpleNamespace(khatmsaz_platform=platform)
        self.message = self
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_bale_invite_is_a_real_clickable_link_not_a_typed_command():
    settings = get_settings()
    assert settings.bale_bot_username, "BALE_BOT_USERNAME must be set for this test to be meaningful"
    set_registry(BotRegistry([SimpleNamespace(
        khatmsaz_role=BotRole.MEMBER,
        khatmsaz_platform=Platform.BALE,
        khatmsaz_category=BotCategory.SALAWAT.value,
        khatmsaz_language="fa",
        khatmsaz_username=settings.bale_bot_username,
    )]))

    chat_id = 9_840_000_777
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, Platform.BALE, chat_id)
        user_id = user.id

    data = {
        "template_type": KhatmTemplateType.SALAWAT.value,
        "khatm_type": KhatmTypeEnum.OPEN.value,
        "title": f"صلوات تست لینک بله {chat_id}",
        "visibility": KhatmVisibility.PUBLIC.value,
        "salawat_open_target": 100,
    }
    message = FakeMessage(chat_id, Platform.BALE)
    await _finish_creating_khatm(message, FakeState(), "fa", data)

    final_text = message.answers[-1][0]
    assert f"https://ble.ir/{settings.bale_bot_username}?start=join_" in final_text
    assert "/start join_" not in final_text.replace(f"?start=join_", "")  # no bare typed-command instruction left

    async with session_scope() as session:
        from sqlalchemy import select
        khatm_row = (await session.execute(select(Khatm).where(Khatm.title == data["title"]))).scalar_one()
        from khatmsaz.modules.invitation.models import KhatmInvitation
        from khatmsaz.modules.audit_log.models import AuditLog
        from khatmsaz.modules.settings.models import UserSettings
        await session.execute(delete(KhatmInvitation).where(KhatmInvitation.khatm_id == khatm_row.id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_row.id))
        await session.execute(delete(AuditLog).where(AuditLog.actor_user_id == user_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
