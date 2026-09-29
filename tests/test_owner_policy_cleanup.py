from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from khatmsaz.bot.handlers import create_khatm
from khatmsaz.bot.handlers.wallet import _localized_amount
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm.quran_editions import CANONICAL_QURAN_EDITION_ID


class FakeState:
    def __init__(self, data):
        self.data = data
        self.state = None

    async def get_data(self):
        return dict(self.data)

    async def update_data(self, **values):
        self.data.update(values)

    async def set_state(self, value):
        self.state = value


@pytest.mark.asyncio
async def test_quran_creation_skips_edition_question(monkeypatch):
    state = FakeState({
        "lang": "fa",
        "template_type": KhatmTemplateType.QURAN_PAGE.value,
        "khatm_type": KhatmTypeEnum.OPEN.value,
    })
    ask_visibility = AsyncMock()
    wizard_message = AsyncMock()
    monkeypatch.setattr(create_khatm, "_ask_visibility", ask_visibility)
    monkeypatch.setattr(create_khatm, "_wiz", wizard_message)

    await create_khatm._after_start_schedule(SimpleNamespace(), state)

    assert state.data["quran_edition_id"] == CANONICAL_QURAN_EDITION_ID
    ask_visibility.assert_awaited_once()
    wizard_message.assert_not_awaited()


def test_creator_contact_is_preserved_outside_editable_welcome():
    stored = "سلام و خوش آمدید\n\n📬 برای ارتباط با سازندهٔ ختم: @owner"
    assert khatm_service.welcome_body_without_contact(stored) == "سلام و خوش آمدید"
    assert khatm_service.preserve_creator_contact(stored, "متن تازه") == (
        "متن تازه\n\n📬 برای ارتباط با سازندهٔ ختم: @owner"
    )
    assert khatm_service.preserve_creator_contact(stored, "") == (
        "📬 برای ارتباط با سازندهٔ ختم: @owner"
    )


def test_wallet_limits_use_local_digits_in_persian():
    assert _localized_amount(10_000, "fa") == "۱۰٬۰۰۰"
    assert _localized_amount(50_000_000, "fa") == "۵۰٬۰۰۰٬۰۰۰"
    assert _localized_amount(10_000, "en") == "10,000"
