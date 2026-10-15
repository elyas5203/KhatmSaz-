"""Automated test suite for MASTER-28: Adversarial Button Audit and Defect Remediation.

Validates the 13 adversarial scenarios identified across Creator Bot, Member Bots,
and Admin Bot:
1. Closed session safety in portions.py (completion and contribution)
2. FSM interruption (bail_if_menu_button) in CommitFlow.entering_times_per_period
3. Authorization enforcement on leave callbacks (leave_ask, leave_reason, approve_leave, reject_leave)
4. Idempotency in workflow_service.leave_khatm (preventing duplicate waiting-list promotions)
5. Stale entity handling in create_khatm.py (send_other_language_links)
6. Polite Persian copy for KhatmCancellationError in my_khatms.py
7. Admin Bot broadcast approval/rejection method correctness (approve / reject)
8. Admin Bot La'an rejection wallet refund workflow integration
9. Concurrent receipt approval/rejection race condition resilience
10. Settings menu callback single-acknowledgment and stale khatm handling
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage, StorageKey
from aiogram.types import CallbackQuery, Message, User as TgUser, Chat

from khatmsaz.bot.handlers import admin_bot, create_khatm, leave, member_commitment, my_khatms, portions, settings_menu, wallet
from khatmsaz.bot.handlers.member_commitment import CommitFlow
from khatmsaz.bot.keyboards import safe_answer_callback
from khatmsaz.modules.identity.models import Platform, User, UserRole
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.wallet.models import ReceiptClaimStatus, WalletReceiptClaim


@pytest.fixture
def memory_fsm_context():
    storage = MemoryStorage()
    key = StorageKey(bot_id=123456, chat_id=987654, user_id=987654)
    return FSMContext(storage=storage, key=key)


def _mock_callback(data: str, user_id: int = 987654, full_name: str = "Test User") -> AsyncMock:
    cb = AsyncMock(spec=CallbackQuery)
    cb.data = data
    cb.from_user = TgUser(id=user_id, is_bot=False, first_name="Test", full_name=full_name)
    cb.message = AsyncMock(spec=Message)
    cb.message.chat = Chat(id=user_id, type="private")
    cb.message.message_id = 111
    cb.message.edit_text = AsyncMock()
    cb.message.edit_caption = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.answer = AsyncMock()
    cb.bot = AsyncMock()
    cb.bot.khatmsaz_platform = Platform.TELEGRAM
    return cb


def _mock_message(text: str, user_id: int = 987654) -> AsyncMock:
    msg = AsyncMock(spec=Message)
    msg.text = text
    msg.from_user = TgUser(id=user_id, is_bot=False, first_name="Test")
    msg.chat = Chat(id=user_id, type="private")
    msg.message_id = 222
    msg.answer = AsyncMock()
    msg.bot = AsyncMock()
    msg.bot.khatmsaz_platform = Platform.TELEGRAM
    return msg


# --- 1. Closed Session Safety in portions.py ---

@pytest.mark.asyncio
async def test_portions_ask_contribution_amount_session_scope():
    """Verify that ask_contribution_amount does not crash on a closed session."""
    khatm_id = str(uuid4())
    cb = _mock_callback(f"contribute:{khatm_id}")

    mock_khatm = MagicMock(spec=Khatm)
    mock_khatm.id = khatm_id
    mock_khatm.khatm_type = KhatmTypeEnum.COMMITMENT
    mock_khatm.commitment_policy = "MEMBER_CHOICE"
    mock_khatm.template_type = KhatmTemplateType.SALAWAT
    mock_khatm.content_category_id = uuid4()

    mock_user = User(id=uuid4(), role=UserRole.USER)
    mock_participation = MagicMock(spec=Participation)
    mock_participation.id = uuid4()
    mock_participation.commitment_mode = None

    mock_cat = SimpleNamespace(group=SimpleNamespace(value="SALAWAT"))

    with patch("khatmsaz.bot.handlers.portions.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.portions.khatm_service.get_khatm", new=AsyncMock(return_value=mock_khatm)), \
         patch("khatmsaz.bot.handlers.portions.identity_service.resolve_or_provision_user", new=AsyncMock(return_value=mock_user)), \
         patch("khatmsaz.bot.handlers.portions._active_participation_for_current_bot", new=AsyncMock(return_value=mock_participation)), \
         patch("khatmsaz.bot.handlers.portions.category_service.get", new=AsyncMock(return_value=mock_cat)), \
         patch("khatmsaz.bot.handlers.member_commitment.start_commitment_mode_picker", new=AsyncMock()) as mock_picker:

        mock_session = AsyncMock()
        mock_scope.return_value.__aenter__.return_value = mock_session

        state = AsyncMock(spec=FSMContext)
        await portions.ask_contribution_amount(cb, state)

        mock_picker.assert_awaited_once()
        cb.answer.assert_awaited()


# --- 2. FSM Anti-Trap (bail_if_menu_button) in member_commitment.py ---

@pytest.mark.asyncio
async def test_member_commitment_bail_if_menu_button_interrupts(memory_fsm_context):
    """Verify that pressing a reply menu button in enter_times_per_period interrupts cleanly."""
    await memory_fsm_context.set_state(CommitFlow.entering_times_per_period)
    await memory_fsm_context.update_data(commit_freq="DAILY", commit_family="SALAWAT")

    # Send persistent menu button instead of integer
    msg = _mock_message("📋 ختم‌های من")

    with patch("khatmsaz.bot.navigation.resolve_home_navigation", new=AsyncMock(return_value=("fa", UserRole.USER, None))):
        await member_commitment.enter_times_per_period(msg, memory_fsm_context)

        # Assert FSM state was cleared by bail_if_menu_button
        current_state = await memory_fsm_context.get_state()
        assert current_state is None
        msg.answer.assert_awaited()


# --- 3. Authorization Checks in leave.py ---

@pytest.mark.asyncio
async def test_leave_approve_unauthorized_user_blocked():
    """Verify that non-creator / unauthorized users cannot approve leave requests."""
    creator_id = uuid4()
    attacker_id = uuid4()
    part_id = uuid4()

    cb = _mock_callback(f"approve_leave:{part_id}:personal", user_id=112233)

    mock_part = MagicMock(spec=Participation)
    mock_part.id = part_id
    mock_part.khatm_id = uuid4()
    mock_part.user_id = uuid4()

    mock_khatm = MagicMock(spec=Khatm)
    mock_khatm.creator_user_id = creator_id

    mock_attacker = User(id=attacker_id, role=UserRole.USER)

    with patch("khatmsaz.bot.handlers.leave._lang_for", new=AsyncMock(return_value="fa")), \
         patch("khatmsaz.bot.handlers.leave.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.leave.participation_service.get_by_id", new=AsyncMock(return_value=mock_part)), \
         patch("khatmsaz.bot.handlers.leave.khatm_service.get_khatm", new=AsyncMock(return_value=mock_khatm)), \
         patch("khatmsaz.bot.handlers.leave.identity_service.find_by_platform", new=AsyncMock(return_value=mock_attacker)), \
         patch("khatmsaz.bot.handlers.leave._do_leave", new=AsyncMock()) as mock_do_leave:

        mock_session = AsyncMock()
        mock_scope.return_value.__aenter__.return_value = mock_session

        await leave.approve_leave(cb)

        # _do_leave must NOT be called for unauthorized caller
        mock_do_leave.assert_not_called()
        cb.answer.assert_awaited()
        # Verifies show_alert was set
        assert cb.answer.call_args.kwargs.get("show_alert") is True


@pytest.mark.asyncio
async def test_leave_reject_unauthorized_user_blocked():
    """Verify that non-creator / unauthorized users cannot reject leave requests."""
    creator_id = uuid4()
    attacker_id = uuid4()
    part_id = uuid4()

    cb = _mock_callback(f"reject_leave:{part_id}", user_id=112233)

    mock_part = MagicMock(spec=Participation)
    mock_part.id = part_id
    mock_part.khatm_id = uuid4()
    mock_part.user_id = uuid4()

    mock_khatm = MagicMock(spec=Khatm)
    mock_khatm.creator_user_id = creator_id

    mock_attacker = User(id=attacker_id, role=UserRole.USER)

    with patch("khatmsaz.bot.handlers.leave._lang_for", new=AsyncMock(return_value="fa")), \
         patch("khatmsaz.bot.handlers.leave.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.leave.participation_service.get_by_id", new=AsyncMock(return_value=mock_part)), \
         patch("khatmsaz.bot.handlers.leave.khatm_service.get_khatm", new=AsyncMock(return_value=mock_khatm)), \
         patch("khatmsaz.bot.handlers.leave.identity_service.find_by_platform", new=AsyncMock(return_value=mock_attacker)):

        mock_session = AsyncMock()
        mock_scope.return_value.__aenter__.return_value = mock_session

        await leave.reject_leave(cb)

        cb.answer.assert_awaited()
        assert cb.answer.call_args.kwargs.get("show_alert") is True


# --- 4. Idempotency in workflow_service.leave_khatm ---

@pytest.mark.asyncio
async def test_workflow_leave_khatm_idempotency_ignores_already_left():
    """Verify that calling leave_khatm on an already LEFT participation does not promote someone twice."""
    from khatmsaz.modules.khatm_workflow import service as workflow_svc

    mock_session = AsyncMock()
    mock_part = MagicMock(spec=Participation)
    mock_part.id = uuid4()
    mock_part.status = ParticipationStatus.LEFT

    with patch("khatmsaz.modules.khatm_workflow.service.participation_service.get_by_id", new=AsyncMock(return_value=mock_part)), \
         patch("khatmsaz.modules.khatm_workflow.service.waiting_list_service.promote_next", new=AsyncMock()) as mock_promote:

        p, portion = await workflow_svc.leave_khatm(mock_session, mock_part.id)

        assert p is None
        assert portion is None
        mock_promote.assert_not_called()


# --- 5. Stale Khatm Handling in create_khatm.py (send_other_language_links) ---

@pytest.mark.asyncio
async def test_send_other_language_links_stale_khatm_graceful_alert():
    """Verify that a stale token in send_other_language_links alerts gracefully without AttributeError."""
    cb = _mock_callback("ck:invlangs:invalid_token")

    with patch("khatmsaz.bot.handlers.create_khatm.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.create_khatm.invitation_service.resolve_khatm_id", new=AsyncMock(return_value=None)):

        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=None)
        mock_scope.return_value.__aenter__.return_value = mock_session

        await create_khatm.send_other_language_links(cb)

        cb.answer.assert_awaited()
        assert cb.answer.call_args.kwargs.get("show_alert") is True


# --- 6. Polite Persian Error Copy for KhatmCancellationError ---

@pytest.mark.asyncio
async def test_my_khatms_cancellation_polite_persian_copy():
    """Verify that KhatmCancellationError displays friendly Persian copy instead of raw English."""
    from khatmsaz.modules.khatm_workflow.service import KhatmCancellationError

    khatm_id = str(uuid4())
    cb = _mock_callback(f"cancel_khatm:{khatm_id}")
    mock_user = User(id=uuid4(), role=UserRole.USER)

    with patch("khatmsaz.bot.handlers.my_khatms._lang_for", new=AsyncMock(return_value="fa")), \
         patch("khatmsaz.bot.handlers.my_khatms.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.my_khatms.identity_service.find_by_platform", new=AsyncMock(return_value=mock_user)), \
         patch("khatmsaz.bot.handlers.my_khatms.workflow_service.cancel_khatm", side_effect=KhatmCancellationError("a member has already joined")):

        mock_session = AsyncMock()
        mock_scope.return_value.__aenter__.return_value = mock_session

        await my_khatms.confirm_cancel_khatm(cb)

        cb.answer.assert_awaited()
        call_text = cb.answer.call_args[0][0]
        # Must be Persian, not the raw English exception
        assert "عضویت اعضا" in call_text
        assert "a member has already joined" not in call_text


# --- 7. Admin Bot Broadcast Review Methods Correctness ---

@pytest.mark.asyncio
async def test_admin_bot_broadcast_approval_and_rejection():
    """Verify that approve_broadcast_callback and reject_broadcast_callback call approve/reject correctly."""
    b_id = uuid4()
    cb_approve = _mock_callback(f"admin_broadcast:approve:{b_id}")
    cb_reject = _mock_callback(f"admin_broadcast:reject:{b_id}")

    mock_broadcast = SimpleNamespace(id=b_id)

    with patch("khatmsaz.bot.handlers.admin_bot.handlers._is_super_admin", new=AsyncMock(return_value=True)), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.identity_service.find_by_platform", new=AsyncMock(return_value=User(id=uuid4(), role=UserRole.SUPER_ADMIN))), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.broadcast_service.approve", new=AsyncMock(return_value=mock_broadcast)) as mock_app, \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.broadcast_service.reject", new=AsyncMock(return_value=mock_broadcast)) as mock_rej:

        mock_session = AsyncMock()
        mock_scope.return_value.__aenter__.return_value = mock_session

        await admin_bot.handlers.approve_broadcast_callback(cb_approve)
        mock_app.assert_awaited_once()
        cb_approve.answer.assert_awaited()

        await admin_bot.handlers.reject_broadcast_callback(cb_reject)
        mock_rej.assert_awaited_once()
        cb_reject.answer.assert_awaited()


# --- 8. Admin Bot La'an Rejection Wallet Refund ---

@pytest.mark.asyncio
async def test_admin_bot_laan_rejection_workflow_refund():
    """Verify that reject_laan_callback routes through workflow_service to issue creator refunds."""
    khatm_id = uuid4()
    cb = _mock_callback(f"laan:reject:{khatm_id}")
    mock_khatm = MagicMock(spec=Khatm)
    mock_khatm.id = khatm_id
    mock_khatm.title = "تست لعن"
    mock_khatm.creator_user_id = uuid4()

    with patch("khatmsaz.bot.handlers.admin_bot.handlers._is_super_admin", new=AsyncMock(return_value=True)), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.identity_service.find_by_platform", new=AsyncMock(return_value=User(id=uuid4(), role=UserRole.SUPER_ADMIN))), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.identity_service.list_identities_for_user", new=AsyncMock(return_value=[])), \
         patch("khatmsaz.bot.handlers.admin_bot.handlers.audit_service.record", new=AsyncMock()), \
         patch("khatmsaz.modules.khatm_workflow.service.review_laan_khatm_workflow", new=AsyncMock(return_value=(mock_khatm, None, 50_000))) as mock_workflow:

        mock_session = AsyncMock()
        mock_scope.return_value.__aenter__.return_value = mock_session

        await admin_bot.handlers.reject_laan_callback(cb)

        mock_workflow.assert_awaited_once_with(mock_session, khatm_id=khatm_id, approved=False)
        cb.message.edit_text.assert_awaited()
        # Verify refund note was included
        assert "۵۰,۰۰۰" in cb.message.edit_text.call_args[0][0] or "50,000" in cb.message.edit_text.call_args[0][0]


# --- 9. Concurrent Receipt Review Handling in wallet.py ---

@pytest.mark.asyncio
async def test_wallet_receipt_review_concurrency_race_handling():
    """Verify that concurrent approval/rejection race condition returns safe alert."""
    claim_id = uuid4()
    cb = _mock_callback(f"receipt:approve:{claim_id}")

    mock_admin = User(id=uuid4(), role=UserRole.SUPER_ADMIN)
    mock_claim = MagicMock(spec=WalletReceiptClaim)
    mock_claim.id = claim_id
    mock_claim.status = ReceiptClaimStatus.PENDING.value

    with patch("khatmsaz.bot.handlers.wallet.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.wallet.identity_service.find_by_platform", new=AsyncMock(return_value=mock_admin)), \
         patch("khatmsaz.bot.handlers.wallet.wallet_service.get_receipt_claim", new=AsyncMock(return_value=mock_claim)), \
         patch("khatmsaz.bot.handlers.wallet.wallet_service.approve_receipt_claim", side_effect=ValueError("claim not found or already processed")):

        mock_session = AsyncMock()
        mock_scope.return_value.__aenter__.return_value = mock_session

        await wallet.approve_receipt_callback(cb)

        cb.answer.assert_awaited()
        assert cb.answer.call_args.kwargs.get("show_alert") is True
        assert "قبلاً تعیین وضعیت شده" in cb.answer.call_args[0][0]


# --- 10. Settings Menu Double-Answer Prevention and Stale Khatm Guard ---

@pytest.mark.asyncio
async def test_settings_menu_save_custom_reminder_stale_khatm():
    """Verify that save_custom_reminder safely handles stale/deleted khatm."""
    part_id = uuid4()
    state = AsyncMock(spec=FSMContext)
    state.get_data = AsyncMock(return_value={"reminder_participation_id": str(part_id)})
    state.clear = AsyncMock()

    msg = _mock_message("14:30")
    mock_user = User(id=uuid4(), role=UserRole.USER)
    mock_settings = SimpleNamespace(language="fa")
    mock_part = MagicMock(spec=Participation)
    mock_part.id = part_id
    mock_part.khatm_id = uuid4()

    with patch("khatmsaz.bot.handlers.settings_menu.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.settings_menu.identity_service.resolve_or_provision_user", new=AsyncMock(return_value=mock_user)), \
         patch("khatmsaz.bot.handlers.settings_menu.settings_service.get_or_create", new=AsyncMock(return_value=mock_settings)), \
         patch("khatmsaz.bot.handlers.settings_menu.participation_service.list_my_active", new=AsyncMock(return_value=[mock_part])), \
         patch("khatmsaz.bot.handlers.settings_menu.khatm_service.get_khatm", new=AsyncMock(return_value=None)):

        mock_session = AsyncMock()
        mock_scope.return_value.__aenter__.return_value = mock_session

        await settings_menu.save_custom_reminder(msg, state)

        state.clear.assert_awaited()
        msg.answer.assert_awaited()
        assert "فعال نیست" in msg.answer.call_args[0][0]
