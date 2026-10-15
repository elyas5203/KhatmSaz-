"""Tests for MASTER-35: Khatm Public Conversion and Link Rotation on Management Delegation."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from khatmsaz.bot.handlers.admin_bot.handlers import approve_transfer_callback
from khatmsaz.bot.handlers.member_start import handle_member_start_with_payload
from khatmsaz.bot.handlers.start import handle_start_with_payload
from khatmsaz.bot.keyboards import public_khatms_keyboard
from khatmsaz.modules.identity.models import Platform, User, UserRole
from khatmsaz.modules.invitation.models import KhatmInvitation
from khatmsaz.modules.invitation.service import (
    InvitationNotFoundError,
    InvitationTransferredError,
    resolve_khatm_id,
    revoke_all_for_khatm,
)
from khatmsaz.modules.khatm.models import (
    Khatm,
    KhatmStatus,
    KhatmTemplateType,
    KhatmTypeEnum,
    KhatmVisibility,
)
from khatmsaz.modules.khatm_workflow import service as workflow_service
from khatmsaz.modules.participation.models import Participation, ParticipationStatus


def _fake_session_scope():
    mock_session = AsyncMock()
    mock_scope = MagicMock()
    mock_scope.__aenter__ = AsyncMock(return_value=mock_session)
    mock_scope.__aexit__ = AsyncMock(return_value=None)
    return mock_scope, mock_session


class FakeMessage:
    def __init__(self, chat_id=12345, text=""):
        self.chat = SimpleNamespace(id=chat_id)
        self.from_user = SimpleNamespace(id=chat_id, full_name="Tester", username="tester")
        self.text = text
        self.bot = SimpleNamespace(
            khatmsaz_platform=Platform.TELEGRAM,
            khatmsaz_language="fa",
            khatmsaz_role="MEMBER",
            khatmsaz_category="salawat",
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
        self.from_user = SimpleNamespace(id=chat_id, full_name="Admin Tester")
        self.message = FakeMessage(chat_id=chat_id)
        self.bot = self.message.bot
        self.answered = False
        self.answered_text = None

    async def answer(self, text=None, show_alert=False):
        self.answered = True
        self.answered_text = text


# ==============================================================================
# 1. LINK ROTATION & PUBLIC CONVERSION IN WORKFLOW SERVICE
# ==============================================================================

@pytest.mark.asyncio
async def test_approve_transfer_revokes_old_links_and_creates_new_public_link():
    """Workflow approval must revoke old tokens, issue a new admin token, and set visibility=PUBLIC."""
    creator_id = uuid4()
    admin_id = uuid4()
    khatm_id = uuid4()

    mock_khatm = Khatm(
        id=khatm_id,
        creator_user_id=creator_id,
        title="ختم صلوات فرج",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
        status=KhatmStatus.ACTIVE,
        visibility=KhatmVisibility.UNLISTED,
        join_link_closed=False,
        transfer_request_status="PENDING",
    )

    mock_session = AsyncMock()
    with patch("khatmsaz.modules.khatm.service.get_khatm_for_update", new_callable=AsyncMock, return_value=mock_khatm), \
         patch("khatmsaz.modules.invitation.service.revoke_all_for_khatm", new_callable=AsyncMock, return_value=3) as mock_revoke, \
         patch("khatmsaz.modules.invitation.service.create_invitation", new_callable=AsyncMock, return_value="shiny_new_admin_token") as mock_create_inv:

        khatm, original_creator_id, new_token = await workflow_service.approve_khatm_transfer(
            mock_session, khatm_id=khatm_id, admin_user_id=admin_id
        )

        assert original_creator_id == creator_id
        assert new_token == "shiny_new_admin_token"
        assert khatm.creator_user_id == admin_id
        assert khatm.transferred_from_user_id == creator_id
        assert khatm.transfer_request_status == "APPROVED"
        assert khatm.visibility == KhatmVisibility.PUBLIC
        assert khatm.join_link_closed is False
        assert khatm.transferred_to_admin_at is not None

        mock_revoke.assert_awaited_once_with(mock_session, khatm_id)
        mock_create_inv.assert_awaited_once_with(mock_session, khatm_id, admin_id)


# ==============================================================================
# 2. RESOLVE_KHATM_ID WITH CANCELLED TOKENS
# ==============================================================================

@pytest.mark.asyncio
async def test_resolve_khatm_id_raises_transferred_error_for_approved_transfer():
    """A cancelled token for an approved transferred khatm raises InvitationTransferredError."""
    khatm_id = uuid4()
    mock_inv = SimpleNamespace(
        khatm_id=khatm_id,
        cancelled_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
    )
    mock_khatm = SimpleNamespace(id=khatm_id, transfer_request_status="APPROVED")

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_khatm)

    with patch("khatmsaz.modules.invitation.repository.get_by_token_hash", new_callable=AsyncMock, return_value=mock_inv):
        with pytest.raises(InvitationTransferredError) as exc_info:
            await resolve_khatm_id(mock_session, "old_revoked_token")

        assert exc_info.value.khatm_id == khatm_id


@pytest.mark.asyncio
async def test_resolve_khatm_id_raises_not_found_for_regular_cancelled_invitation():
    """A cancelled token for a khatm that was not transferred raises InvitationNotFoundError."""
    khatm_id = uuid4()
    mock_inv = SimpleNamespace(
        khatm_id=khatm_id,
        cancelled_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
    )
    mock_khatm = SimpleNamespace(id=khatm_id, transfer_request_status="NONE")

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_khatm)

    with patch("khatmsaz.modules.invitation.repository.get_by_token_hash", new_callable=AsyncMock, return_value=mock_inv):
        with pytest.raises(InvitationNotFoundError):
            await resolve_khatm_id(mock_session, "ordinary_cancelled_token")


# ==============================================================================
# 3. MEMBER START HANDLER ON OLD CANCELLED LINK
# ==============================================================================

@pytest.mark.asyncio
async def test_member_start_old_link_allows_existing_active_participant():
    """An existing member clicking an old cancelled link is NOT blocked and continues recitation."""
    khatm_id = uuid4()
    user_id = uuid4()

    mock_khatm = SimpleNamespace(
        id=khatm_id,
        title="ختم صلوات عمومی",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
        status=KhatmStatus.ACTIVE,
        join_link_closed=False,
        visibility=KhatmVisibility.PUBLIC,
        allowed_platforms="BOTH",
        content_category_id=None,
        creator_user_id=uuid4(),
        niyyat=None,
        deadline=None,
        welcome_text=None,
        repetition_target=None,
        rules_text=None,
    )
    mock_user = SimpleNamespace(id=user_id, display_name="Zahra")
    mock_part = SimpleNamespace(id=uuid4(), status=ParticipationStatus.ACTIVE)

    msg = FakeMessage(chat_id=777)
    command = SimpleNamespace(args="join_old_creator_token")
    state = MagicMock()
    state.clear = AsyncMock()
    state.update_data = AsyncMock()

    scope, mock_sess = _fake_session_scope()

    with patch("khatmsaz.bot.handlers.member_start.session_scope", return_value=scope), \
         patch("khatmsaz.modules.identity.service.resolve_or_provision_user", new_callable=AsyncMock, return_value=mock_user), \
         patch("khatmsaz.modules.invitation.service.resolve_khatm_id", new_callable=AsyncMock, side_effect=InvitationTransferredError(khatm_id)), \
         patch("khatmsaz.modules.khatm.service.get_khatm", new_callable=AsyncMock, return_value=mock_khatm), \
         patch("khatmsaz.modules.participation.service.get_active", new_callable=AsyncMock, return_value=mock_part), \
         patch("khatmsaz.bot.handlers.member_start._matches_member_bot", new_callable=AsyncMock, return_value=True), \
         patch("khatmsaz.modules.identity.service.find_by_id", new_callable=AsyncMock, return_value=SimpleNamespace(display_name="خدمتگزاران تک")), \
         patch("khatmsaz.modules.participation.service.count_for_khatm", new_callable=AsyncMock, return_value=15):

        await handle_member_start_with_payload(msg, command, state)

    assert len(msg.answers) >= 1
    sent_text = msg.answers[-1][0]
    assert "شما از قبل عضو فعال این ختم هستید" in sent_text
    assert "خدمتگزاران تک" in sent_text


@pytest.mark.asyncio
async def test_member_start_old_link_informs_new_user_and_offers_public_join():
    """A new user clicking an old cancelled link is informed of the transfer and given the new public link."""
    khatm_id = uuid4()
    user_id = uuid4()

    mock_khatm = SimpleNamespace(
        id=khatm_id,
        title="ختم صلوات عمومی",
        template_type=KhatmTemplateType.SALAWAT,
        status=KhatmStatus.ACTIVE,
        visibility=KhatmVisibility.PUBLIC,
        content_category_id=None,
        creator_user_id=uuid4(),
    )
    mock_user = SimpleNamespace(id=user_id, display_name="Reza")

    msg = FakeMessage(chat_id=888)
    command = SimpleNamespace(args="join_old_creator_token")
    state = MagicMock()
    state.clear = AsyncMock()

    scope, mock_sess = _fake_session_scope()

    with patch("khatmsaz.bot.handlers.member_start.session_scope", return_value=scope), \
         patch("khatmsaz.modules.identity.service.resolve_or_provision_user", new_callable=AsyncMock, return_value=mock_user), \
         patch("khatmsaz.modules.invitation.service.resolve_khatm_id", new_callable=AsyncMock, side_effect=InvitationTransferredError(khatm_id)), \
         patch("khatmsaz.modules.khatm.service.get_khatm", new_callable=AsyncMock, return_value=mock_khatm), \
         patch("khatmsaz.modules.participation.service.get_active", new_callable=AsyncMock, return_value=None), \
         patch("khatmsaz.modules.invitation.service.get_or_create_for_khatm", new_callable=AsyncMock, return_value="new_public_token_777"), \
         patch("khatmsaz.bot.invite_links.resolve_khatm_category_value", new_callable=AsyncMock, return_value="salawat"), \
         patch("khatmsaz.bot.invite_links.build_member_invite_links", return_value={"fa": "https://t.me/salawat_bot?start=new_public_token_777"}), \
         patch("khatmsaz.bot.invite_links.format_invite_lines", return_value="🔗 https://t.me/salawat_bot?start=new_public_token_777"):

        await handle_member_start_with_payload(msg, command, state)

    assert len(msg.answers) >= 1
    sent_text, reply_markup, _ = msg.answers[-1]
    assert "مدیریت این ختم به مجموعه «خدمتگزاران تک» واگذار شده است" in sent_text
    assert "لینک ورود قبلی منقضی گردیده است" in sent_text
    assert "https://t.me/salawat_bot?start=new_public_token_777" in sent_text
    # Inline button offered
    assert reply_markup is not None
    button_texts = [btn.text for row in reply_markup.inline_keyboard for btn in row]
    assert "🌱 پیوستن به این ختم عمومی" in button_texts


# ==============================================================================
# 4. CREATOR/GENERAL BOT START HANDLER ON OLD CANCELLED LINK
# ==============================================================================

@pytest.mark.asyncio
async def test_start_py_handles_invitation_transferred_error():
    """Start in general bot clicking transferred link informs user and provides member links."""
    khatm_id = uuid4()
    user_id = uuid4()

    mock_khatm = SimpleNamespace(
        id=khatm_id,
        title="ختم صلوات عمومی",
        template_type=KhatmTemplateType.SALAWAT,
        status=KhatmStatus.ACTIVE,
        visibility=KhatmVisibility.PUBLIC,
        content_category_id=None,
        creator_user_id=uuid4(),
    )
    mock_user = SimpleNamespace(id=user_id, display_name="Hossein", role=UserRole.USER)

    msg = FakeMessage(chat_id=999)
    command = SimpleNamespace(args="join_old_creator_token")
    state = MagicMock()
    state.clear = AsyncMock()

    scope, mock_sess = _fake_session_scope()

    with patch("khatmsaz.bot.handlers.start.session_scope", return_value=scope), \
         patch("khatmsaz.modules.identity.service.resolve_or_provision_user", new_callable=AsyncMock, return_value=mock_user), \
         patch("khatmsaz.modules.settings.service.get_or_create", new_callable=AsyncMock, return_value=SimpleNamespace(language="fa")), \
         patch("khatmsaz.modules.invitation.service.resolve_khatm_id", new_callable=AsyncMock, side_effect=InvitationTransferredError(khatm_id)), \
         patch("khatmsaz.modules.khatm.service.get_khatm", new_callable=AsyncMock, return_value=mock_khatm), \
         patch("khatmsaz.modules.invitation.service.get_or_create_for_khatm", new_callable=AsyncMock, return_value="new_tok_start"), \
         patch("khatmsaz.bot.invite_links.resolve_khatm_category_value", new_callable=AsyncMock, return_value="salawat"), \
         patch("khatmsaz.bot.invite_links.build_member_invite_links", return_value={"fa": "https://t.me/salawat_bot?start=new_tok_start"}), \
         patch("khatmsaz.bot.invite_links.format_invite_lines", return_value="🔗 https://t.me/salawat_bot?start=new_tok_start"):

        await handle_start_with_payload(msg, command, state)

    assert len(msg.answers) >= 1
    sent_text = msg.answers[-1][0]
    assert "مدیریت این ختم به مجموعه «خدمتگزاران تک» واگذار شده است" in sent_text
    assert "https://t.me/salawat_bot?start=new_tok_start" in sent_text


# ==============================================================================
# 5. PUBLIC LISTING & KEYBOARD BADGE
# ==============================================================================

def test_public_khatms_keyboard_adds_badge_for_transferred_khatms():
    """public_khatms_keyboard must add '🤝 [عمومی - تک] ' for transferred khatms."""
    regular_khatm = SimpleNamespace(
        id=uuid4(),
        title="ختم عمومی عادی",
        transfer_request_status="NONE",
        transferred_from_user_id=None,
    )
    transferred_khatm = SimpleNamespace(
        id=uuid4(),
        title="ختم صلوات واگذار شده",
        transfer_request_status="APPROVED",
        transferred_from_user_id=uuid4(),
    )

    kb = public_khatms_keyboard([regular_khatm, transferred_khatm])
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]

    assert "🌱 پیوستن به «ختم عمومی عادی»" in button_texts
    assert "🤝 [عمومی - تک] «ختم صلوات واگذار شده»" in button_texts
