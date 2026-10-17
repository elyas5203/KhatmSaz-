"""Tests for MASTER-33: Khatm Deactivation & Management Delegation to Service Admin (Rule 5)."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from bs4 import BeautifulSoup
from starlette.testclient import TestClient

from khatmsaz.bot.handlers.admin_bot.handlers import (
    approve_transfer_callback,
    reject_transfer_callback,
    show_pending_transfers,
)
from khatmsaz.bot.handlers.member_start import handle_member_start_with_payload
from khatmsaz.bot.handlers.my_khatms import (
    on_khatm_transfer_ask,
    on_khatm_transfer_cancel,
    on_khatm_transfer_confirm,
    on_khatm_transfer_dismiss,
)
from khatmsaz.bot.keyboards import creator_khatm_keyboard, khatm_transfer_confirm_keyboard
from khatmsaz.modules.identity.models import Platform, User, UserRole
from khatmsaz.modules.khatm.models import (
    Khatm,
    KhatmStatus,
    KhatmTemplateType,
    KhatmTypeEnum,
    KhatmVisibility,
)
from khatmsaz.modules.khatm_workflow import service as workflow_service
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.web.app import app


def _fake_session_scope():
    mock_session = AsyncMock()
    mock_scope = MagicMock()
    mock_scope.__aenter__ = AsyncMock(return_value=mock_session)
    mock_scope.__aexit__ = AsyncMock(return_value=None)
    return mock_scope, mock_session


class FakeMessage:
    def __init__(self, chat_id=12345, text=""):
        self.chat = SimpleNamespace(id=chat_id)
        self.from_user = SimpleNamespace(id=chat_id, full_name="User Test")
        self.text = text
        self.bot = SimpleNamespace(
            khatmsaz_platform=Platform.TELEGRAM,
            khatmsaz_language="fa",
            khatmsaz_role="CREATOR",
            khatmsaz_category=None,
        )
        self.answers = []

    async def answer(self, text, reply_markup=None, **kwargs):
        self.answers.append((text, reply_markup, kwargs))
        return self

    async def edit_text(self, text, reply_markup=None, **kwargs):
        self.answers.append((text, reply_markup, kwargs))
        return self

    async def delete(self):
        pass


class FakeCallback:
    def __init__(self, data="", chat_id=12345):
        self.data = data
        self.from_user = SimpleNamespace(id=chat_id, full_name="Creator User")
        self.message = FakeMessage(chat_id=chat_id)
        self.bot = self.message.bot
        self.answered = False
        self.answered_text = None

    async def answer(self, text=None, show_alert=False):
        self.answered = True
        self.answered_text = text


# ==============================================================================
# 1. KEYBOARD UNIT TESTS
# ==============================================================================

def test_creator_khatm_keyboard_shows_transfer_button():
    """Creator keyboard must show [🤝 واگذاری مدیریت به پشتیبانی] when status is NONE, and never show cancel khatm."""
    kb = creator_khatm_keyboard("test-id", can_cancel=True, transfer_status="NONE", lang="fa")
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]
    button_callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]

    assert "🤝 واگذاری مدیریت به پشتیبانی" in button_texts
    assert "khatm_transfer_ask:test-id" in button_callbacks
    assert "cancel_khatm_ask:test-id" not in button_callbacks
    assert "my_khatms:open" in button_callbacks


def test_creator_khatm_keyboard_shows_cancel_transfer_when_pending():
    """Creator keyboard must show [⏳ لغو درخواست واگذاری مدیریت] when transfer is PENDING, and never show cancel khatm."""
    kb = creator_khatm_keyboard("test-id", can_cancel=True, transfer_status="PENDING", lang="fa")
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]
    button_callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]

    assert "⏳ لغو درخواست واگذاری مدیریت" in button_texts
    assert "khatm_transfer_cancel:test-id" in button_callbacks
    assert "cancel_khatm_ask:test-id" not in button_callbacks
    assert "my_khatms:open" in button_callbacks


def test_khatm_transfer_confirm_keyboard_layout():
    """Confirmation keyboard must have confirm and dismiss callbacks."""
    kb = khatm_transfer_confirm_keyboard("test-id", lang="fa")
    button_callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]

    assert "khatm_transfer_confirm:test-id" in button_callbacks
    assert "khatm_transfer_dismiss:test-id" in button_callbacks


# ==============================================================================
# 2. WORKFLOW SERVICE UNIT TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_workflow_transfer_request_and_cancel():
    """request_khatm_transfer sets PENDING, cancel_khatm_transfer_request resets to NONE."""
    creator_id = uuid4()
    khatm_id = uuid4()
    mock_khatm = Khatm(
        id=khatm_id,
        creator_user_id=creator_id,
        title="ختم تست واگذاری",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
        status=KhatmStatus.ACTIVE,
        transfer_request_status="NONE",
    )

    mock_session = AsyncMock()
    with patch("khatmsaz.modules.khatm.service.get_khatm_for_update", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_khatm

        # 1. Request transfer
        updated = await workflow_service.request_khatm_transfer(
            mock_session, khatm_id=khatm_id, creator_user_id=creator_id, reason="عدم فرصت کافی"
        )
        assert updated.transfer_request_status == "PENDING"
        assert updated.transfer_request_reason == "عدم فرصت کافی"
        assert updated.transfer_requested_at is not None

        # Duplicate request should raise KhatmTransferError
        with pytest.raises(workflow_service.KhatmTransferError):
            await workflow_service.request_khatm_transfer(
                mock_session, khatm_id=khatm_id, creator_user_id=creator_id
            )

        # 2. Cancel transfer
        cancelled = await workflow_service.cancel_khatm_transfer_request(
            mock_session, khatm_id=khatm_id, creator_user_id=creator_id
        )
        assert cancelled.transfer_request_status == "NONE"
        assert cancelled.transfer_request_reason is None


@pytest.mark.asyncio
async def test_workflow_approve_transfer_closes_link_and_assigns_admin():
    """Approving transfer sets APPROVED, rotates link, sets PUBLIC, and transfers ownership to admin."""
    creator_id = uuid4()
    admin_id = uuid4()
    khatm_id = uuid4()
    mock_khatm = Khatm(
        id=khatm_id,
        creator_user_id=creator_id,
        title="ختم تست تأیید واگذاری",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
        status=KhatmStatus.ACTIVE,
        transfer_request_status="PENDING",
        join_link_closed=False,
    )

    mock_session = AsyncMock()
    with patch("khatmsaz.modules.khatm.service.get_khatm_for_update", new_callable=AsyncMock) as mock_get, \
         patch("khatmsaz.modules.invitation.service.revoke_all_for_khatm", new_callable=AsyncMock) as mock_revoke, \
         patch("khatmsaz.modules.invitation.service.create_invitation", new_callable=AsyncMock, return_value="new_admin_token_456"):
        mock_get.return_value = mock_khatm

        approved_khatm, original_id, new_token = await workflow_service.approve_khatm_transfer(
            mock_session, khatm_id=khatm_id, admin_user_id=admin_id
        )
        assert original_id == creator_id
        assert new_token == "new_admin_token_456"
        assert approved_khatm.transfer_request_status == "APPROVED"
        assert approved_khatm.join_link_closed is False
        assert approved_khatm.visibility == KhatmVisibility.PUBLIC
        assert approved_khatm.creator_user_id == admin_id
        assert approved_khatm.transferred_from_user_id == creator_id
        assert approved_khatm.transferred_to_admin_at is not None
        mock_revoke.assert_awaited_once_with(mock_session, khatm_id)


# ==============================================================================
# 3. CREATOR BOT HANDLER TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_creator_bot_transfer_ask_renders_rule_5():
    """Clicking khatm_transfer_ask shows Persian explanation citing Rule 5."""
    creator_id = uuid4()
    khatm_id = uuid4()
    mock_khatm = SimpleNamespace(
        id=khatm_id,
        title="ختم صلوات فرج",
        creator_user_id=creator_id,
        status=KhatmStatus.ACTIVE,
        transfer_request_status="NONE",
    )

    cb = FakeCallback(data=f"khatm_transfer_ask:{khatm_id}")
    scope, mock_sess = _fake_session_scope()

    with patch("khatmsaz.bot.handlers.my_khatms._owned_khatm_for_callback", new_callable=AsyncMock) as mock_owned, \
         patch("khatmsaz.bot.handlers.my_khatms.session_scope", return_value=scope), \
         patch("khatmsaz.bot.handlers.my_khatms._lang_for", new_callable=AsyncMock, return_value="fa"), \
         patch("khatmsaz.modules.participation.service.count_for_khatm", new_callable=AsyncMock, return_value=42):
        mock_owned.return_value = (creator_id, mock_khatm)

        await on_khatm_transfer_ask(cb)

    assert len(cb.message.answers) >= 1
    sent_text = cb.message.answers[-1][0]
    assert "بند ۵ قوانین و مقررات ختم‌ساز" in sent_text
    assert "خدمتگزاران تک" in sent_text
    assert "42" in sent_text
    assert "لینک عضویت قبلی شما منقضی شده" in sent_text
    assert "اعضای قبلی از ختم خارج نخواهند شد" in sent_text


@pytest.mark.asyncio
async def test_creator_bot_transfer_confirm_alerts_super_admins():
    """Confirming transfer requests transfer in workflow and notifies super admins."""
    creator_id = uuid4()
    khatm_id = uuid4()
    mock_khatm = SimpleNamespace(
        id=khatm_id,
        title="ختم صلوات فرج",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
        creator_user_id=creator_id,
    )
    mock_user = SimpleNamespace(id=creator_id, display_name="Ali")

    cb = FakeCallback(data=f"khatm_transfer_confirm:{khatm_id}")
    scope, mock_sess = _fake_session_scope()

    with patch("khatmsaz.bot.handlers.my_khatms.session_scope", return_value=scope), \
         patch("khatmsaz.bot.handlers.my_khatms._lang_for", new_callable=AsyncMock, return_value="fa"), \
         patch("khatmsaz.modules.identity.service.find_by_platform", new_callable=AsyncMock, return_value=mock_user), \
         patch("khatmsaz.modules.khatm_workflow.service.request_khatm_transfer", new_callable=AsyncMock, return_value=mock_khatm), \
         patch("khatmsaz.modules.participation.service.count_for_khatm", new_callable=AsyncMock, return_value=10), \
         patch("khatmsaz.bot.handlers.my_khatms.notify_super_admins", new_callable=AsyncMock) as mock_notify:

        await on_khatm_transfer_confirm(cb)
        mock_notify.assert_awaited_once()

    sent_text = cb.message.answers[-1][0]
    assert "با موفقیت ثبت شد و برای پشتیبانی خدمتگزاران تک ارسال گردید" in sent_text


# ==============================================================================
# 4. ADMIN BOT MODERATION HANDLER TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_admin_bot_approve_transfer():
    """Admin approving transfer rotates link, reassigns ownership, makes public, and updates message."""
    khatm_id = uuid4()
    creator_id = uuid4()
    admin_id = uuid4()
    mock_khatm = SimpleNamespace(
        id=khatm_id,
        title="ختم صلوات",
        template_type=KhatmTemplateType.SALAWAT,
        content_category_id=None,
        allowed_platforms="BOTH",
    )
    mock_admin = SimpleNamespace(id=admin_id)

    cb = FakeCallback(data=f"admin_transfer:approve:{khatm_id}")
    scope, mock_sess = _fake_session_scope()

    with patch("khatmsaz.bot.handlers.admin_bot.handlers._is_super_admin", new_callable=AsyncMock, return_value=True), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.session_scope", return_value=scope), \
         patch("khatmsaz.modules.identity.service.find_by_platform", new_callable=AsyncMock, return_value=mock_admin), \
         patch("khatmsaz.modules.khatm_workflow.service.approve_khatm_transfer", new_callable=AsyncMock) as mock_approve, \
         patch("khatmsaz.bot.invite_links.resolve_khatm_category_value", new_callable=AsyncMock, return_value="salawat"), \
         patch("khatmsaz.bot.invite_links.build_member_invite_links", return_value={"fa": "https://t.me/salawat_bot?start=new_tok"}), \
         patch("khatmsaz.bot.invite_links.format_invite_lines", return_value="🔗 https://t.me/salawat_bot?start=new_tok"), \
         patch("khatmsaz.modules.audit_log.service.record", new_callable=AsyncMock):

        mock_approve.return_value = (mock_khatm, creator_id, "new_tok")
        await approve_transfer_callback(cb)

    assert cb.answered is True
    sent_text = cb.message.answers[-1][0]
    assert "با موفقیت به خدمتگزاران تک واگذار شد" in sent_text
    assert "عمومی (Public)" in sent_text
    assert "لینک قبلی سازنده:</b> منقضی و لغو گردید" in sent_text
    assert "https://t.me/salawat_bot?start=new_tok" in sent_text


# ==============================================================================
# 5. MEMBER JOIN GATE (CLOSED LINK BEHAVIOR)
# ==============================================================================

@pytest.mark.asyncio
async def test_member_join_closed_link_blocks_new_member():
    """A new user clicking a join link where join_link_closed=True gets blocked."""
    khatm_id = uuid4()
    user_id = uuid4()
    mock_khatm = SimpleNamespace(
        id=khatm_id,
        status=KhatmStatus.ACTIVE,
        join_link_closed=True,
        allowed_platforms="BOTH",
    )
    mock_user = SimpleNamespace(id=user_id)

    msg = FakeMessage(chat_id=998877)
    command = SimpleNamespace(args="join_token123")
    state = MagicMock()
    state.clear = AsyncMock()
    state.update_data = AsyncMock()

    scope, mock_sess = _fake_session_scope()

    with patch("khatmsaz.bot.handlers.member_start.session_scope", return_value=scope), \
         patch("khatmsaz.modules.identity.service.resolve_or_provision_user", new_callable=AsyncMock, return_value=mock_user), \
         patch("khatmsaz.modules.invitation.service.resolve_khatm_id", new_callable=AsyncMock, return_value=khatm_id), \
         patch("khatmsaz.modules.khatm.service.get_khatm", new_callable=AsyncMock, return_value=mock_khatm), \
         patch("khatmsaz.modules.participation.service.get_active", new_callable=AsyncMock, return_value=None):

        await handle_member_start_with_payload(msg, command, state)

    assert len(msg.answers) >= 1
    sent_text = msg.answers[-1][0]
    assert "امکان عضویت جدید در این ختم وجود ندارد" in sent_text
    assert "لینک عضویت این ختم توسط مدیریت بسته شده است" in sent_text


@pytest.mark.asyncio
async def test_member_join_closed_link_allows_existing_member():
    """An existing member clicking a closed link is NOT blocked."""
    khatm_id = uuid4()
    user_id = uuid4()
    mock_khatm = SimpleNamespace(
        id=khatm_id,
        title="ختم فرج",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
        status=KhatmStatus.ACTIVE,
        join_link_closed=True,
        allowed_platforms="BOTH",
        content_category_id=None,
        creator_user_id=uuid4(),
        niyyat=None,
        deadline=None,
        visibility=KhatmVisibility.PUBLIC,
        welcome_text=None,
        repetition_target=None,
        rules_text=None,
    )
    mock_user = SimpleNamespace(id=user_id)
    mock_participation = SimpleNamespace(id=uuid4(), status=ParticipationStatus.ACTIVE)

    msg = FakeMessage(chat_id=998877)
    command = SimpleNamespace(args="join_token123")
    state = MagicMock()
    state.clear = AsyncMock()
    state.update_data = AsyncMock()

    scope, mock_sess = _fake_session_scope()

    with patch("khatmsaz.bot.handlers.member_start.session_scope", return_value=scope), \
         patch("khatmsaz.modules.identity.service.resolve_or_provision_user", new_callable=AsyncMock, return_value=mock_user), \
         patch("khatmsaz.modules.invitation.service.resolve_khatm_id", new_callable=AsyncMock, return_value=khatm_id), \
         patch("khatmsaz.modules.khatm.service.get_khatm", new_callable=AsyncMock, return_value=mock_khatm), \
         patch("khatmsaz.modules.participation.service.get_active", new_callable=AsyncMock, return_value=mock_participation), \
         patch("khatmsaz.bot.handlers.member_start._matches_member_bot", new_callable=AsyncMock, return_value=True), \
         patch("khatmsaz.modules.identity.service.find_by_id", new_callable=AsyncMock, return_value=SimpleNamespace(display_name="Admin")), \
         patch("khatmsaz.modules.participation.service.count_for_khatm", new_callable=AsyncMock, return_value=10):

        await handle_member_start_with_payload(msg, command, state)

    assert len(msg.answers) >= 1
    sent_text = msg.answers[-1][0]
    # Did not block!
    assert "امکان عضویت جدید در این ختم وجود ندارد" not in sent_text


# ==============================================================================
# 6. WEB ROUTES AND TEMPLATES
# ==============================================================================

def test_web_creator_transfer_request_route():
    """POST /creator/khatms/{khatm_id}/transfer/request invokes workflow and notifies admin."""
    client = TestClient(app)
    khatm_id = uuid4()
    creator_id = uuid4()
    mock_creator = SimpleNamespace(id=creator_id, role=UserRole.CREATOR, display_name="Creator Ali")
    mock_khatm = SimpleNamespace(
        id=khatm_id,
        title="ختم صلوات",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
    )
    scope, mock_sess = _fake_session_scope()

    with patch("khatmsaz.web.app._creator", new_callable=AsyncMock, return_value=(mock_creator, "raw_session", "fa")), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", return_value=scope), \
         patch("khatmsaz.modules.khatm_workflow.service.request_khatm_transfer", new_callable=AsyncMock, return_value=mock_khatm), \
         patch("khatmsaz.modules.participation.service.count_for_khatm", new_callable=AsyncMock, return_value=5), \
         patch("khatmsaz.bot.admin_notifications.notify_super_admins", new_callable=AsyncMock) as mock_notify, \
         patch("khatmsaz.modules.audit_log.service.record", new_callable=AsyncMock):

        res = client.post(
            f"/creator/khatms/{khatm_id}/transfer/request",
            data={"csrf": "dummy_csrf"},
            follow_redirects=False,
        )
        assert res.status_code == 303
        assert f"/creator/khatms/{khatm_id}?saved=transfer_requested" in res.headers["location"]
        mock_notify.assert_awaited_once()


def test_web_admin_transfer_approve_route():
    """POST /khatms/{khatm_id}/transfer/approve calls workflow and redirects."""
    client = TestClient(app)
    khatm_id = uuid4()
    admin_id = uuid4()
    creator_id = uuid4()
    mock_admin = SimpleNamespace(id=admin_id, role=UserRole.SUPER_ADMIN)
    mock_khatm = SimpleNamespace(id=khatm_id, title="ختم صلوات")
    scope, mock_sess = _fake_session_scope()

    with patch("khatmsaz.web.app._admin", new_callable=AsyncMock, return_value=(mock_admin, "raw_session")), \
         patch("khatmsaz.web.app._valid_csrf", return_value=True), \
         patch("khatmsaz.web.app.session_scope", return_value=scope), \
         patch("khatmsaz.modules.khatm_workflow.service.approve_khatm_transfer", new_callable=AsyncMock, return_value=(mock_khatm, creator_id, "new_tok")), \
         patch("khatmsaz.modules.audit_log.service.record", new_callable=AsyncMock):

        res = client.post(
            f"/khatms/{khatm_id}/transfer/approve",
            data={"csrf": "dummy_csrf"},
            follow_redirects=False,
        )
        assert res.status_code == 303
        assert f"/khatms/{khatm_id}?saved=transfer_approved" in res.headers["location"]


def test_web_templates_contain_transfer_management_elements():
    """creator_khatm_detail.html, khatm_detail.html and khatms.html must contain transfer cards and badges."""
    with open("src/khatmsaz/web/templates/creator_khatm_detail.html", "r", encoding="utf-8") as f:
        creator_detail = f.read()
    assert "واگذاری مدیریت ختم و تبدیل به ختم عمومی (بند ۵ قوانین)" in creator_detail
    assert "/transfer/request" in creator_detail
    assert "/transfer/cancel" in creator_detail

    with open("src/khatmsaz/web/templates/khatm_detail.html", "r", encoding="utf-8") as f:
        admin_detail = f.read()
    assert "درخواست واگذاری مدیریت ختم به خدمتگزاران تک (بند ۵ قوانین)" in admin_detail
    assert "/transfer/approve" in admin_detail
    assert "/transfer/reject" in admin_detail

    with open("src/khatmsaz/web/templates/khatms.html", "r", encoding="utf-8") as f:
        khatms_html = f.read()
    assert "🤝 درخواست واگذاری" in khatms_html
