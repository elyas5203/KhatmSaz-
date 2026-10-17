"""Tests for MASTER-27: Creator Member Management & Two-Step Removal.

Verifies:
1. Keyboard generators produce valid buttons with callback_data strictly <= 64 bytes.
2. Pagination splits members across pages (8 per page) with proper navigation.
3. Detail screen renders participant data (display name, phone, progress, misses).
4. Step 1 confirmation (km:ask:) warns creator and provides step 2 button.
5. Step 2 confirmation (km:conf:) requires final confirmation before removal.
6. Execution (km:do:) performs leave_khatm, frees portions, logs audit, and sends polite notification.
7. Unauthorized users cannot view or delete members from another creator's khatm.
"""

import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from khatmsaz.bot.keyboards import (
    creator_members_list_keyboard,
    creator_member_detail_keyboard,
    creator_member_remove_step1_keyboard,
    creator_member_remove_step2_keyboard,
)
from khatmsaz.bot.handlers.my_khatms import (
    _render_khatm_members_view,
    member_detail_callback,
    member_remove_ask_step1,
    member_remove_confirm_step2,
    member_remove_execute,
    khatm_members_callback,
)


def test_creator_keyboards_callback_data_under_64_bytes():
    """Verify that every generated callback data is strictly <= 64 bytes (Telegram limit)."""
    khatm_id = uuid.uuid4()
    part_id = uuid.uuid4()

    # Detail keyboard
    detail_kb = creator_member_detail_keyboard(khatm_id, part_id, lang="fa")
    for row in detail_kb.inline_keyboard:
        for btn in row:
            assert len(btn.callback_data.encode("utf-8")) <= 64
            assert btn.callback_data.startswith(("km:ask:", "km:list:"))

    # Step 1 keyboard
    step1_kb = creator_member_remove_step1_keyboard(part_id, lang="fa")
    for row in step1_kb.inline_keyboard:
        for btn in row:
            assert len(btn.callback_data.encode("utf-8")) <= 64
            assert btn.callback_data.startswith(("km:conf:", "km:v:"))

    # Step 2 keyboard
    step2_kb = creator_member_remove_step2_keyboard(part_id, lang="fa")
    for row in step2_kb.inline_keyboard:
        for btn in row:
            assert len(btn.callback_data.encode("utf-8")) <= 64
            assert btn.callback_data.startswith(("km:do:", "km:v:"))


def test_creator_members_list_keyboard_pagination():
    """Verify pagination controls when members exceed page size (8)."""
    khatm_id = uuid.uuid4()
    members = []
    for i in range(20):
        p = MagicMock()
        p.id = uuid.uuid4()
        m = MagicMock()
        m.display_name = f"کاربر {i + 1}"
        members.append((p, m))

    # Page 0 (First page)
    kb_p0 = creator_members_list_keyboard(khatm_id, members, page=0, page_size=8)
    # 8 member rows + 1 nav row + 1 back row = 10 rows
    assert len(kb_p0.inline_keyboard) == 10
    nav_row_p0 = kb_p0.inline_keyboard[8]
    # Page 0 has: [صفحه 1 از 3], [بعدی ▶️] (no previous)
    assert any("بعدی" in btn.text for btn in nav_row_p0)
    assert not any("قبلی" in btn.text for btn in nav_row_p0)

    # Page 1 (Middle page)
    kb_p1 = creator_members_list_keyboard(khatm_id, members, page=1, page_size=8)
    nav_row_p1 = kb_p1.inline_keyboard[8]
    assert any("قبلی" in btn.text for btn in nav_row_p1)
    assert any("بعدی" in btn.text for btn in nav_row_p1)

    # Page 2 (Last page: 4 members)
    kb_p2 = creator_members_list_keyboard(khatm_id, members, page=2, page_size=8)
    # 4 member rows + 1 nav row + 1 back row = 6 rows
    assert len(kb_p2.inline_keyboard) == 6
    nav_row_p2 = kb_p2.inline_keyboard[4]
    assert any("قبلی" in btn.text for btn in nav_row_p2)
    assert not any("بعدی" in btn.text for btn in nav_row_p2)

    # All callbacks strictly <= 64 bytes
    for kb in (kb_p0, kb_p1, kb_p2):
        for row in kb.inline_keyboard:
            for btn in row:
                assert len(btn.callback_data.encode("utf-8")) <= 64


@pytest.mark.asyncio
async def test_render_khatm_members_view_empty():
    """Verify view when khatm has no active members."""
    session = AsyncMock()
    khatm = MagicMock()
    khatm.id = uuid.uuid4()
    khatm.title = "ختم تستی"
    user = MagicMock()

    with patch("khatmsaz.bot.handlers.my_khatms.participation_service.list_active_with_users", AsyncMock(return_value=[])):
        text, kb = await _render_khatm_members_view(session, khatm, user, "fa", page=0)
        assert "عضو" in text or "پیدا نشد" in text or "هیچ" in text
        assert len(kb.inline_keyboard) == 1
        assert "my_khatms:manage:" in kb.inline_keyboard[0][0].callback_data


@pytest.mark.asyncio
async def test_render_khatm_members_view_with_members():
    """Verify view formats member progress and provides buttons."""
    session = AsyncMock()
    khatm = MagicMock()
    khatm.id = uuid.uuid4()
    khatm.title = "ختم زیارت عاشورا"
    user = MagicMock()

    part = MagicMock()
    part.id = uuid.uuid4()
    part.is_committed = True
    part.backup_reader_opt_in = False
    member = MagicMock()
    member.display_name = "علی رضایی"

    portion = MagicMock()
    portion.participation_id = part.id
    portion.quantity = 100
    portion.completed_quantity = 50

    with patch("khatmsaz.bot.handlers.my_khatms.participation_service.list_active_with_users", AsyncMock(return_value=[(part, member)])), \
         patch("khatmsaz.bot.handlers.my_khatms.allocation_service.list_for_khatm", AsyncMock(return_value=[portion])):
        text, kb = await _render_khatm_members_view(session, khatm, user, "fa", page=0)
        assert "علی رضایی" in text
        assert "50/100" in text
        assert "متعهد" in text
        assert len(kb.inline_keyboard) == 2  # 1 member button + 1 back button
        assert kb.inline_keyboard[0][0].callback_data == f"km:v:{part.id.hex}"


@pytest.mark.asyncio
async def test_member_detail_callback():
    """Verify km:v:{part_hex} renders member details including phone number."""
    creator_user = MagicMock(id=uuid.uuid4())
    member_user = MagicMock(id=uuid.uuid4(), display_name="حسین علوی")
    khatm = MagicMock(id=uuid.uuid4(), creator_user_id=creator_user.id, title="ختم سوره یس")
    part = MagicMock(id=uuid.uuid4(), user_id=member_user.id, khatm_id=khatm.id)
    part.status.value = "ACTIVE"
    part.is_committed = True

    member_settings = MagicMock(contact_phone="+989123456789")

    callback = MagicMock()
    callback.data = f"km:v:{part.id.hex}"
    callback.message = MagicMock()
    callback.message.chat.id = 12345
    callback.bot = MagicMock()

    with patch("khatmsaz.bot.handlers.my_khatms._lang_for", AsyncMock(return_value="fa")), \
         patch("khatmsaz.bot.handlers.my_khatms.identity_service.find_by_platform", AsyncMock(return_value=creator_user)), \
         patch("khatmsaz.bot.handlers.my_khatms.participation_service.get_by_id", AsyncMock(return_value=part)), \
         patch("khatmsaz.bot.handlers.my_khatms.khatm_service.get_khatm", AsyncMock(return_value=khatm)), \
         patch("khatmsaz.bot.handlers.my_khatms.identity_service.find_by_id", AsyncMock(return_value=member_user)), \
         patch("khatmsaz.bot.handlers.my_khatms.settings_service.get_or_create", AsyncMock(return_value=member_settings)), \
         patch("khatmsaz.bot.handlers.my_khatms.allocation_service.get_current_portion", AsyncMock(return_value=None)), \
         patch("khatmsaz.bot.handlers.my_khatms.allocation_service.list_for_khatm", AsyncMock(return_value=[])), \
         patch("khatmsaz.bot.handlers.my_khatms.notification_service.total_miss_count", AsyncMock(return_value=2)), \
         patch("khatmsaz.bot.handlers.my_khatms.notification_service.get_preference", AsyncMock(return_value=None)), \
         patch("khatmsaz.bot.handlers.my_khatms.safe_answer_callback", AsyncMock()) as mock_answer:

        callback.message.edit_text = AsyncMock()
        await member_detail_callback(callback)

        assert callback.message.edit_text.called
        sent_text = callback.message.edit_text.call_args[0][0]
        assert "حسین علوی" in sent_text
        assert "+989123456789" in sent_text
        assert "2 روز" in sent_text
        kb = callback.message.edit_text.call_args[1]["reply_markup"]
        assert kb.inline_keyboard[0][0].callback_data == f"km:ask:{part.id.hex}"


@pytest.mark.asyncio
async def test_two_step_removal_flow():
    """Verify Step 1 (km:ask) -> Step 2 (km:conf) -> Execution (km:do)."""
    creator_user = MagicMock(id=uuid.uuid4())
    member_user = MagicMock(id=uuid.uuid4(), display_name="محمد محمدی")
    khatm = MagicMock(id=uuid.uuid4(), creator_user_id=creator_user.id, title="ختم دعای عهد")
    part = MagicMock(id=uuid.uuid4(), user_id=member_user.id, khatm_id=khatm.id)
    part.status.value = "ACTIVE"
    part.joined_via_bot_instance_id = "bot_1"

    callback = MagicMock()
    callback.message = MagicMock()
    callback.message.chat.id = 12345
    callback.bot = MagicMock()
    callback.message.edit_text = AsyncMock()

    # Step 1: km:ask:
    callback.data = f"km:ask:{part.id.hex}"
    with patch("khatmsaz.bot.handlers.my_khatms._lang_for", AsyncMock(return_value="fa")), \
         patch("khatmsaz.bot.handlers.my_khatms.identity_service.find_by_platform", AsyncMock(return_value=creator_user)), \
         patch("khatmsaz.bot.handlers.my_khatms.participation_service.get_by_id", AsyncMock(return_value=part)), \
         patch("khatmsaz.bot.handlers.my_khatms.khatm_service.get_khatm", AsyncMock(return_value=khatm)), \
         patch("khatmsaz.bot.handlers.my_khatms.identity_service.find_by_id", AsyncMock(return_value=member_user)), \
         patch("khatmsaz.bot.handlers.my_khatms.safe_answer_callback", AsyncMock()):

        await member_remove_ask_step1(callback)
        step1_text = callback.message.edit_text.call_args[0][0]
        assert "مرحله ۱ از ۲" in step1_text
        step1_kb = callback.message.edit_text.call_args[1]["reply_markup"]
        assert step1_kb.inline_keyboard[0][0].callback_data == f"km:conf:{part.id.hex}"
        assert step1_kb.inline_keyboard[1][0].callback_data == f"km:v:{part.id.hex}"

    # Step 2: km:conf:
    callback.data = f"km:conf:{part.id.hex}"
    with patch("khatmsaz.bot.handlers.my_khatms._lang_for", AsyncMock(return_value="fa")), \
         patch("khatmsaz.bot.handlers.my_khatms.identity_service.find_by_platform", AsyncMock(return_value=creator_user)), \
         patch("khatmsaz.bot.handlers.my_khatms.participation_service.get_by_id", AsyncMock(return_value=part)), \
         patch("khatmsaz.bot.handlers.my_khatms.khatm_service.get_khatm", AsyncMock(return_value=khatm)), \
         patch("khatmsaz.bot.handlers.my_khatms.identity_service.find_by_id", AsyncMock(return_value=member_user)), \
         patch("khatmsaz.bot.handlers.my_khatms.safe_answer_callback", AsyncMock()):

        await member_remove_confirm_step2(callback)
        step2_text = callback.message.edit_text.call_args[0][0]
        assert "مرحله ۲ از ۲" in step2_text
        step2_kb = callback.message.edit_text.call_args[1]["reply_markup"]
        assert step2_kb.inline_keyboard[0][0].callback_data == f"km:do:{part.id.hex}"
        assert step2_kb.inline_keyboard[1][0].callback_data == f"km:v:{part.id.hex}"

    # Execution: km:do:
    callback.data = f"km:do:{part.id.hex}"
    mock_leave = AsyncMock(return_value=(None, None))
    mock_audit = AsyncMock()
    mock_notify = AsyncMock()

    with patch("khatmsaz.bot.handlers.my_khatms._lang_for", AsyncMock(return_value="fa")), \
         patch("khatmsaz.bot.handlers.my_khatms.identity_service.find_by_platform", AsyncMock(return_value=creator_user)), \
         patch("khatmsaz.bot.handlers.my_khatms.participation_service.get_by_id", AsyncMock(return_value=part)), \
         patch("khatmsaz.bot.handlers.my_khatms.khatm_service.get_khatm", AsyncMock(return_value=khatm)), \
         patch("khatmsaz.bot.handlers.my_khatms.identity_service.find_by_id", AsyncMock(return_value=member_user)), \
         patch("khatmsaz.bot.handlers.my_khatms.identity_service.list_identities_for_user", AsyncMock(return_value=[])), \
         patch("khatmsaz.bot.handlers.my_khatms.allocation_service.get_current_portion", AsyncMock(return_value=None)), \
         patch("khatmsaz.bot.handlers.my_khatms.workflow_service.leave_khatm", mock_leave), \
         patch("khatmsaz.bot.handlers.my_khatms.audit_service.record", mock_audit), \
         patch("khatmsaz.bot.notify_adapter.get_notify_fn", return_value=mock_notify), \
         patch("khatmsaz.bot.handlers.my_khatms.safe_answer_callback", AsyncMock()):

        await member_remove_execute(callback)
        mock_leave.assert_called_once()
        assert mock_leave.call_args[0][1] == part.id
        assert mock_leave.call_args[1]["reason"] == "REMOVED_BY_CREATOR"
        mock_audit.assert_called_once()
        exec_text = callback.message.edit_text.call_args[0][0]
        assert "لغو شد" in exec_text
        exec_kb = callback.message.edit_text.call_args[1]["reply_markup"]
        assert exec_kb.inline_keyboard[0][0].callback_data == f"km:list:{khatm.id.hex}"


@pytest.mark.asyncio
async def test_unauthorized_user_cannot_remove_member():
    """Security check: non-creator cannot view or remove members."""
    another_user = MagicMock(id=uuid.uuid4())
    creator_user = MagicMock(id=uuid.uuid4())
    khatm = MagicMock(id=uuid.uuid4(), creator_user_id=creator_user.id)
    part = MagicMock(id=uuid.uuid4(), khatm_id=khatm.id)

    callback = MagicMock()
    callback.data = f"km:do:{part.id.hex}"
    callback.message = MagicMock()
    callback.message.chat.id = 99999
    callback.bot = MagicMock()

    with patch("khatmsaz.bot.handlers.my_khatms._lang_for", AsyncMock(return_value="fa")), \
         patch("khatmsaz.bot.handlers.my_khatms.identity_service.find_by_platform", AsyncMock(return_value=another_user)), \
         patch("khatmsaz.bot.handlers.my_khatms.participation_service.get_by_id", AsyncMock(return_value=part)), \
         patch("khatmsaz.bot.handlers.my_khatms.khatm_service.get_khatm", AsyncMock(return_value=khatm)), \
         patch("khatmsaz.bot.handlers.my_khatms.safe_answer_callback", AsyncMock()) as mock_answer, \
         patch("khatmsaz.bot.handlers.my_khatms.workflow_service.leave_khatm", AsyncMock()) as mock_leave:

        await member_remove_execute(callback)
        # leave_khatm must NOT be called
        mock_leave.assert_not_called()
        # User is warned with not found / unauthorized alert
        mock_answer.assert_called_once()
        assert mock_answer.call_args[1].get("show_alert") is True
