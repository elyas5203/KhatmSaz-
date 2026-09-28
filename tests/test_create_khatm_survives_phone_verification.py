"""Owner-reported bug (2026-09-21/22): a first-time creator with an
unverified phone used to lose their ENTIRE create-khatm wizard the moment
`confirm_wizard` discovered their phone wasn't verified — told to run
`/verify_phone` and start the whole wizard over from scratch. This
confirms the fix: `confirm_wizard` now kicks off the same OTP flow but
keeps the wizard's answers, and once the OTP code is entered correctly,
the khatm actually gets created with those preserved answers — no restart
needed. See `bot/handlers/create_khatm.py::resume_khatm_creation_if_pending`."""

from types import SimpleNamespace

import pytest
from sqlalchemy import delete, select

from khatmsaz.bot.handlers.change_phone import ChangePhone, receive_change_code
from khatmsaz.bot.handlers.create_khatm import CreateKhatm, confirm_wizard
from khatmsaz.core.db import session_scope
from khatmsaz.core.bot_registry import BotRegistry, set_registry
from khatmsaz.config import get_settings
from khatmsaz.modules.bot_registry.models import BotCategory, BotRole
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User
from khatmsaz.modules.khatm.models import Khatm, KhatmTemplateType, KhatmTypeEnum, KhatmVisibility
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.settings.models import Gender


class FakeState:
    def __init__(self, data):
        self.data = data
        self.state = "seed"

    async def get_data(self):
        return dict(self.data)

    async def update_data(self, **values):
        self.data.update(values)

    async def set_state(self, value):
        self.state = value

    async def get_state(self):
        return self.state

    async def clear(self):
        self.data = {}
        self.state = None


class FakeMessage:
    def __init__(self, chat_id):
        self.chat = SimpleNamespace(id=chat_id)
        self.bot = SimpleNamespace(khatmsaz_platform=Platform.TELEGRAM)
        self.message = self
        self.text = None
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))

    async def edit_reply_markup(self, **kwargs):
        pass


class FakeCallback:
    def __init__(self, chat_id):
        self.message = FakeMessage(chat_id)
        self.from_user = SimpleNamespace(id=chat_id)

    async def answer(self, *a, **k):
        pass


@pytest.mark.integration
async def test_confirm_wizard_resumes_and_finishes_creation_after_otp():
    import time
    unique = str(int(time.time() * 1000))[-8:]
    settings = get_settings()
    set_registry(BotRegistry([SimpleNamespace(
        khatmsaz_role=BotRole.MEMBER,
        khatmsaz_platform=Platform.TELEGRAM,
        khatmsaz_category=BotCategory.SALAWAT.value,
        khatmsaz_language="fa",
        khatmsaz_username=settings.telegram_bot_username or "test_salawat_bot",
    )]))
    chat_id = int(f"98{unique}")
    phone = f"+989{unique}"
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, Platform.TELEGRAM, chat_id)
        from khatmsaz.modules.identity.models import UserRole
        user.role = UserRole.CREATOR
        await identity_service.set_display_name(session, user.id, "کاربر تست")
        await settings_service.save_profile(
            session, user.id, contact_phone=phone, province="تهران", city="تهران", gender=Gender.MALE,
        )
        user_id = user.id

    wizard_data = {
        "lang": "fa",
        "template_type": KhatmTemplateType.SALAWAT.value,
        "khatm_type": KhatmTypeEnum.OPEN.value,
        "title": f"صلوات تست بازیابی بعد از تأیید شماره {unique}",
        "visibility": KhatmVisibility.PUBLIC.value,
        "salawat_open_target": 100,
    }
    state = FakeState(dict(wizard_data))
    callback = FakeCallback(chat_id)

    await confirm_wizard(callback, state)

    # Phone wasn't verified yet — an OTP step should now be active, and the
    # wizard's own answers must still be sitting in state (not thrown away).
    assert state.state == ChangePhone.entering_code
    assert state.data.get("resume_khatm_creation") is True
    assert state.data.get("title") == wizard_data["title"]
    assert any("دیجیت" in text or len(text) > 0 for text, _ in callback.message.answers)

    async with session_scope() as session:
        no_khatm_yet = (
            await session.execute(select(Khatm).where(Khatm.title == wizard_data["title"]))
        ).scalar_one_or_none()
        assert no_khatm_yet is None

    # Extract the dev-mode OTP code the bot just sent (DEV_OTP=1 in this
    # local environment embeds it directly in the message text).
    sent_text = callback.message.answers[-1][0]
    import re
    match = re.search(r"(\d{6})", sent_text)
    assert match, f"couldn't find a 6-digit OTP code in: {sent_text!r}"
    code = match.group(1)

    otp_message = FakeMessage(chat_id)
    otp_message.text = code
    await receive_change_code(otp_message, state)

    # The khatm should now actually exist, built from the ORIGINAL wizard
    # answers — no "start over" required.
    async with session_scope() as session:
        khatm = (
            await session.execute(select(Khatm).where(Khatm.title == wizard_data["title"]))
        ).scalar_one_or_none()
        assert khatm is not None
        assert khatm.creator_user_id == user_id
        assert khatm.template_type == KhatmTemplateType.SALAWAT

        from khatmsaz.modules.phone.models import OtpChallenge, PhoneClaim
        from khatmsaz.modules.wallet.models import Wallet, WalletTransaction
        from khatmsaz.modules.invitation.models import KhatmInvitation
        from khatmsaz.modules.settings.models import UserSettings
        await session.execute(delete(KhatmInvitation).where(KhatmInvitation.khatm_id == khatm.id))
        wallet_ids = (await session.execute(select(Wallet.id).where(Wallet.user_id == user_id))).scalars().all()
        if wallet_ids:
            await session.execute(delete(WalletTransaction).where(WalletTransaction.wallet_id.in_(wallet_ids)))
            await session.execute(delete(Wallet).where(Wallet.id.in_(wallet_ids)))
        await session.execute(delete(Khatm).where(Khatm.id == khatm.id))
        from khatmsaz.modules.audit_log.models import AuditLog
        await session.execute(delete(AuditLog).where(AuditLog.actor_user_id == user_id))
        await session.execute(delete(OtpChallenge).where(OtpChallenge.user_id == user_id))
        await session.execute(delete(PhoneClaim).where(PhoneClaim.user_id == user_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(PlatformIdentity).where(PlatformIdentity.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))
