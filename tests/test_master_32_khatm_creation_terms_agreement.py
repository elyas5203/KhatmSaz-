"""Tests for MASTER-32: Mandatory Terms & Rules Agreement during Khatm Creation,
and Dedicated Video Creation Entry Points.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from bs4 import BeautifulSoup
from starlette.testclient import TestClient

from khatmsaz.bot.handlers.create_khatm import (
    CreateKhatm,
    accept_rules_and_finish_khatm,
    back_to_confirm_details,
    confirm_wizard,
)
from khatmsaz.bot.keyboards import confirm_keyboard, rules_agreement_keyboard
from khatmsaz.i18n import t
from khatmsaz.modules.identity.models import Platform, User, UserRole
from khatmsaz.modules.khatm.models import (
    Khatm,
    KhatmTemplateType,
    KhatmTypeEnum,
    KhatmVisibility,
)
from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup
from khatmsaz.web.app import app


def _fake_session_scope():
    mock_session = AsyncMock()
    mock_scope = MagicMock()
    mock_scope.__aenter__ = AsyncMock(return_value=mock_session)
    mock_scope.__aexit__ = AsyncMock(return_value=None)
    return mock_scope, mock_session


class FakeFSMContext:
    def __init__(self, data=None, state=None):
        self._data = data or {}
        self._state = state

    async def get_data(self):
        return dict(self._data)

    async def update_data(self, **kwargs):
        self._data.update(kwargs)

    async def set_state(self, state):
        self._state = state

    async def get_state(self):
        return getattr(self._state, "state", self._state)

    async def clear(self):
        self._data.clear()
        self._state = None


class FakeMessage:
    def __init__(self, chat_id=12345):
        self.chat = SimpleNamespace(id=chat_id)
        self.message_id = 999
        self.from_user = SimpleNamespace(id=chat_id, first_name="TestCreator")
        self.bot = SimpleNamespace(
            khatmsaz_platform=Platform.TELEGRAM,
            delete_message=AsyncMock(),
            edit_message_text=AsyncMock(),
        )
        self.answers = []

    async def answer(self, text, **kwargs):
        self.answers.append((text, kwargs))
        msg = SimpleNamespace(
            message_id=len(self.answers) + 1000,
            text=text,
            delete=AsyncMock(),
        )
        return msg

    async def delete(self):
        pass


class FakeCallback:
    def __init__(self, data="ck:confirm", chat_id=12345):
        self.data = data
        self.from_user = SimpleNamespace(id=chat_id, first_name="TestCreator")
        self.message = FakeMessage(chat_id)

    async def answer(self, *args, **kwargs):
        pass


@pytest.mark.asyncio
async def test_confirm_wizard_transitions_to_rules_agreement():
    """When creator clicks 'ck:confirm', bot must transition to confirming_rules and display the 6 rules."""
    chat_id = 556677
    state = FakeFSMContext(
        data={
            "lang": "fa",
            "title": "ختم تست قوانین",
            "template_type": KhatmTemplateType.SALAWAT.value,
            "khatm_type": KhatmTypeEnum.OPEN.value,
            "visibility": KhatmVisibility.UNLISTED.value,
        },
        state=CreateKhatm.confirming,
    )
    callback = FakeCallback(data="ck:confirm", chat_id=chat_id)

    with patch("khatmsaz.bot.handlers.change_phone.ensure_creator_phone_verified", new_callable=AsyncMock) as mock_phone:
        mock_phone.return_value = True
        await confirm_wizard(callback, state)

    # State must be confirming_rules
    assert await state.get_state() == CreateKhatm.confirming_rules.state

    # Message must contain the 6 rules and key contact information
    assert len(callback.message.answers) >= 1
    sent_text = callback.message.answers[-1][0]
    assert "قوانین و مقررات ایجاد و مدیریت ختم" in sent_text
    assert "اعضای هر ختم متعلق به سازنده آن ختم هستند" in sent_text
    assert "ارسال پیام گروهی" in sent_text
    assert "خدمتگزاران تک" in sent_text
    assert "هزینه آبونمان" in sent_text
    assert "+989051240561" in sent_text

    # Keyboard must have ck:accept_rules button
    kb = callback.message.answers[-1][1].get("reply_markup")
    assert kb is not None
    button_callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    assert "ck:accept_rules" in button_callbacks
    assert "ck:back_to_confirm" in button_callbacks
    assert "ck:cancel" in button_callbacks


@pytest.mark.asyncio
async def test_accept_rules_and_finish_khatm():
    """Clicking 'ck:accept_rules' marks rules as accepted and calls _finish_creating_khatm."""
    chat_id = 556678
    state = FakeFSMContext(
        data={
            "lang": "fa",
            "title": "ختم تست پذیرش قوانین",
            "template_type": KhatmTemplateType.SALAWAT.value,
            "khatm_type": KhatmTypeEnum.OPEN.value,
            "visibility": KhatmVisibility.UNLISTED.value,
        },
        state=CreateKhatm.confirming_rules,
    )
    callback = FakeCallback(data="ck:accept_rules", chat_id=chat_id)

    with patch("khatmsaz.bot.handlers.change_phone.ensure_creator_phone_verified", new_callable=AsyncMock) as mock_phone, \
         patch("khatmsaz.bot.handlers.create_khatm._finish_creating_khatm", new_callable=AsyncMock) as mock_finish:
        mock_phone.return_value = True
        await accept_rules_and_finish_khatm(callback, state)

        data = await state.get_data()
        assert data.get("rules_accepted") is True
        assert "rules_accepted_at" in data
        mock_finish.assert_awaited_once()


@pytest.mark.asyncio
async def test_back_to_confirm_details_from_rules():
    """Clicking 'ck:back_to_confirm' re-renders the confirmation overview screen."""
    chat_id = 556679
    state = FakeFSMContext(
        data={
            "lang": "fa",
            "title": "ختم بازگشت",
            "template_type": KhatmTemplateType.SALAWAT.value,
            "khatm_type": KhatmTypeEnum.OPEN.value,
            "visibility": KhatmVisibility.UNLISTED.value,
        },
        state=CreateKhatm.confirming_rules,
    )
    callback = FakeCallback(data="ck:back_to_confirm", chat_id=chat_id)

    with patch("khatmsaz.bot.handlers.create_khatm._show_confirmation", new_callable=AsyncMock) as mock_show:
        await back_to_confirm_details(callback, state)
        mock_show.assert_awaited_once()


def test_web_creator_khatm_create_requires_accept_rules():
    """Submitting creator khatm create form without accept_rules redirects with terms_required error."""
    client = TestClient(app)
    mock_creator = SimpleNamespace(
        id=uuid4(),
        role=UserRole.CREATOR,
        telegram_id=123456,
        display_name="Creator User",
    )

    with patch("khatmsaz.web.app._creator", new_callable=AsyncMock) as mock_auth, \
         patch("khatmsaz.web.app._valid_csrf", return_value=True):
        mock_auth.return_value = (mock_creator, "raw_session", "fa")

        # Missing accept_rules
        res = client.post(
            "/creator/khatms/create",
            data={
                "csrf": "dummy_csrf",
                "content_kind": "salawat",
                "khatm_type": "OPEN",
                "title": "ختم تستی بدون قوانین",
                "amount": "1000",
                "visibility": "UNLISTED",
            },
            follow_redirects=False,
        )
        assert res.status_code == 303
        assert "/creator/khatms/new?error=terms_required" in res.headers["location"]


def test_web_creator_khatm_create_accepts_when_rules_checked():
    """Submitting creator khatm create form with accept_rules='1' proceeds past the rules gate."""
    client = TestClient(app)
    mock_creator = SimpleNamespace(
        id=uuid4(),
        role=UserRole.CREATOR,
        telegram_id=123456,
        display_name="Creator User",
    )
    scope, mock_sess = _fake_session_scope()

    with patch("khatmsaz.web.app._creator", new_callable=AsyncMock) as mock_auth, \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", return_value=scope), \
         patch("khatmsaz.web.app.settings_repository.get_by_user", new_callable=AsyncMock, return_value=None), \
         patch("khatmsaz.web.app.phone_repository.verified_claim_for_user", new_callable=AsyncMock) as mock_phone:
        mock_auth.return_value = (mock_creator, "raw_session", "fa")
        # Ensure it does not fail on terms_required
        mock_phone.return_value = None  # Will fail at phone check instead of terms_required

        res = client.post(
            "/creator/khatms/create",
            data={
                "csrf": "dummy_csrf",
                "content_kind": "salawat",
                "khatm_type": "OPEN",
                "title": "ختم تستی با قوانین",
                "amount": "1000",
                "visibility": "UNLISTED",
                "accept_rules": "1",
            },
            follow_redirects=False,
        )
        assert res.status_code == 303
        # Failed at phone check, NOT terms_required, proving terms_required passed!
        assert "/creator/khatms/new?error=phone" in res.headers["location"]


def test_web_templates_contain_terms():
    """HTML templates must render the 6 terms and the accept_rules checkbox."""
    with open("src/khatmsaz/web/templates/creator_khatm_new.html", "r", encoding="utf-8") as f:
        new_html = f.read()

    assert "قوانین و مقررات ایجاد و مدیریت ختم" in new_html
    assert "name=\"accept_rules\"" in new_html
    assert "اعضای هر ختم متعلق به سازنده آن ختم هستند" in new_html
    assert "ارسال پیام گروهی" in new_html
    assert "خدمتگزاران تک" in new_html
    assert "+98 905 124 0561" in new_html
    assert "terms_required" in new_html
