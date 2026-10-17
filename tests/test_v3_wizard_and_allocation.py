"""Tests for V3 Wizard flow, 2-message finish, editing from confirm, and sequential allocation priority."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User

from khatmsaz.bot.handlers.create_khatm import (
    CANONICAL_QURAN_EDITION_ID,
    CreateKhatm,
    enter_edited_title,
    finish_invite_links,
    handle_edit_field_choice,
    show_edit_menu,
)
from khatmsaz.bot.keyboards import edit_khatm_fields_keyboard
from khatmsaz.modules.khatm.models import (
    Khatm,
    KhatmTemplateType,
    KhatmTypeEnum,
)
from khatmsaz.modules.share_occurrence import delivery


class DummyState:
    def __init__(self, data: dict | None = None, state: str | None = None):
        self._data = data or {}
        self._state = state

    async def get_data(self) -> dict:
        return dict(self._data)

    async def update_data(self, **kwargs) -> None:
        self._data.update(kwargs)

    async def set_state(self, state) -> None:
        self._state = state.state if hasattr(state, "state") else state

    async def get_state(self) -> str | None:
        return self._state

    async def clear(self) -> None:
        self._data.clear()
        self._state = None


@pytest.mark.asyncio
async def test_finish_invite_links_sends_two_messages():
    """V3 WP-07: finish_invite_links must send two messages:

    1. Creator greeting + home menu
    2. Forwardable invite card without system text, without duplicate 'ختم ختم', and with disabled link preview.
    """
    khatm = MagicMock(spec=Khatm)
    khatm.id = uuid.uuid4()
    khatm.title = "صلوات برای فرج"
    khatm.niyyat = "به نیابت از مرحوم پدرم"
    khatm.khatm_type = KhatmTypeEnum.COMMITMENT
    khatm.template_type = KhatmTemplateType.SALAWAT

    msg = AsyncMock(spec=Message)
    msg.answer = AsyncMock()

    state = DummyState(
        data={
            "created_khatm_id": khatm.id,
            "created_token": "token123",
            "selected_invite_languages": ["fa"],
            "selected_invite_platform": "ALL",
        }
    )

    with patch("khatmsaz.bot.handlers.create_khatm.session_scope") as mock_scope, \
         patch("khatmsaz.bot.handlers.create_khatm.invite_links") as mock_invite_links:

        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=khatm)
        mock_scope.return_value.__aenter__.return_value = mock_session

        mock_invite_links.resolve_khatm_category_value = AsyncMock(return_value="SALAWAT")
        mock_invite_links.build_member_invite_links.return_value = {"fa": {"TELEGRAM": "https://t.me/khatm_bot?start=k_token123"}}
        mock_invite_links.format_invite_lines.return_value = "https://t.me/khatm_bot?start=k_token123"

        await finish_invite_links(msg, state, lang="fa")  # type: ignore

    # Must call msg.answer twice: Message 1 (creator confirmation) & Message 2 (forwardable card)
    assert msg.answer.call_count == 2

    call_1 = msg.answer.call_args_list[0]
    call_2 = msg.answer.call_args_list[1]

    text_1 = call_1.args[0] if call_1.args else call_1.kwargs.get("text", "")
    text_2 = call_2.args[0] if call_2.args else call_2.kwargs.get("text", "")

    # Message 1: Creator greeting + reply keyboard
    assert "ثبت شد" in text_1 or "موفقیت" in text_1 or "صلوات برای فرج" in text_1
    assert "reply_markup" in call_1.kwargs

    # Message 2: Forwardable card
    assert "ختم ختم" not in text_2
    assert "صلوات برای فرج" in text_2
    assert "ظهور منجی عالم بشریت" in text_2
    assert "مرحوم پدرم" in text_2
    assert "https://t.me/khatm_bot?start=k_token123" in text_2
    assert "📖 نوع ختم: صلوات" in text_2
    assert "🌿 شیوهٔ برگزاری: تعهدی" in text_2

    # Link preview must be disabled on message 2
    link_preview = call_2.kwargs.get("link_preview_options")
    assert link_preview is not None
    assert getattr(link_preview, "is_disabled", False) is True


@pytest.mark.asyncio
async def test_editing_from_confirm_title_flow():
    """V3 WP-06: Editing a field from confirmation screen returns directly to confirm screen."""
    # 1. User clicks ck:edit_menu from confirm screen
    cb_menu = AsyncMock(spec=CallbackQuery)
    cb_menu.data = "ck:edit_menu"
    cb_menu.message = AsyncMock(spec=Message)
    cb_menu.message.chat = MagicMock(id=100)
    cb_menu.message.bot = AsyncMock()
    cb_menu.message.answer = AsyncMock()
    cb_menu.answer = AsyncMock()

    state = DummyState(
        data={"title": "عنوان اولیه", "editing_from_confirm": False},
        state=CreateKhatm.confirming.state,
    )

    with patch("khatmsaz.bot.handlers.create_khatm._wiz", new_callable=AsyncMock) as mock_wiz:
        await show_edit_menu(cb_menu, state)  # type: ignore
        mock_wiz.assert_called_once()
        assert mock_wiz.call_args.kwargs.get("reply_markup") == edit_khatm_fields_keyboard("fa")

    # 2. User chooses ck:edit:title
    cb_field = AsyncMock(spec=CallbackQuery)
    cb_field.data = "ck:edit:title"
    cb_field.message = AsyncMock(spec=Message)
    cb_field.message.chat = MagicMock(id=100)
    cb_field.message.bot = AsyncMock()
    cb_field.answer = AsyncMock()

    with patch("khatmsaz.bot.handlers.create_khatm._wiz", new_callable=AsyncMock) as mock_wiz_field:
        await handle_edit_field_choice(cb_field, state)  # type: ignore
        assert await state.get_state() == CreateKhatm.editing_title.state
        data = await state.get_data()
        assert data.get("editing_from_confirm") is True
        mock_wiz_field.assert_called_once()

    # 3. User submits new title
    msg_title = AsyncMock(spec=Message)
    msg_title.text = "عنوان جدید پس از ویرایش"
    msg_title.from_user = MagicMock(spec=User)
    msg_title.from_user.id = 999
    msg_title.bot = MagicMock()

    with patch("khatmsaz.bot.handlers.create_khatm._show_confirmation") as mock_show_confirm:
        await enter_edited_title(msg_title, state)  # type: ignore
        mock_show_confirm.assert_called_once()

    data_after = await state.get_data()
    assert data_after.get("title") == "عنوان جدید پس از ویرایش"
    assert data_after.get("editing_from_confirm") is False


@pytest.mark.asyncio
async def test_sequential_candidate_ids_priority():
    """V3 Sequential allocation: earlier hour gets priority, then earlier joined_at."""
    session = AsyncMock()
    result_mock = MagicMock()
    p1 = uuid.uuid4()
    p2 = uuid.uuid4()
    result_mock.scalars.return_value = [p1, p2]
    session.execute = AsyncMock(return_value=result_mock)

    candidates = await delivery.candidate_ids(session)
    assert candidates == [p1, p2]

    # Verify query was constructed with order_by
    call_arg = session.execute.call_args[0][0]
    sql_str = str(call_arg.compile(compile_kwargs={"literal_binds": False}))
    # Assert ORDER BY clause contains coalesce for hour, and joined_at
    assert "ORDER BY" in sql_str
    assert "joined_at" in sql_str
    assert "coalesce" in sql_str.lower()


@pytest.mark.asyncio
async def test_previous_wizard_step_comprehensive_flow():
    """Verify that clicking ck:back steps backward step-by-step through all wizard states without jumping to template."""
    from khatmsaz.bot.handlers.create_khatm import previous_wizard_step
    from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup

    cb = AsyncMock(spec=CallbackQuery)
    cb.data = "ck:back"
    cb.from_user = MagicMock(id=555)
    cb.message = AsyncMock(spec=Message)
    cb.message.chat = MagicMock(id=555)
    cb.message.bot = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.answer = AsyncMock()

    with patch("khatmsaz.bot.handlers.create_khatm._wiz", new_callable=AsyncMock) as mock_wiz, \
         patch("khatmsaz.bot.handlers.create_khatm.safe_clear_inline_keyboard", new_callable=AsyncMock):

        # 1. From confirming -> choosing_visibility
        state = DummyState(data={}, state=CreateKhatm.confirming.state)
        await previous_wizard_step(cb, state)
        assert await state.get_state() == CreateKhatm.choosing_visibility.state

        # 2. From choosing_visibility -> choosing_reminder_tone
        state = DummyState(data={}, state=CreateKhatm.choosing_visibility.state)
        await previous_wizard_step(cb, state)
        assert await state.get_state() == CreateKhatm.choosing_reminder_tone.state

        # 3. From choosing_reminder_tone (Commitment + FIXED_DAILY) -> entering_fixed_daily_amount
        state = DummyState(
            data={"khatm_type": KhatmTypeEnum.COMMITMENT.value, "commitment_policy": "FIXED_DAILY"},
            state=CreateKhatm.choosing_reminder_tone.state,
        )
        await previous_wizard_step(cb, state)
        assert await state.get_state() == CreateKhatm.entering_fixed_daily_amount.state

        # 4. From entering_fixed_daily_amount -> choosing_commitment_policy
        state = DummyState(data={}, state=CreateKhatm.entering_fixed_daily_amount.state)
        await previous_wizard_step(cb, state)
        assert await state.get_state() == CreateKhatm.choosing_commitment_policy.state

        # 5. From choosing_commitment_policy (Salawat) -> choosing_commitment_total
        state = DummyState(
            data={"template_type": KhatmTemplateType.SALAWAT.value, "category_group": KhatmCategoryGroup.SALAWAT.value},
            state=CreateKhatm.choosing_commitment_policy.state,
        )
        await previous_wizard_step(cb, state)
        assert await state.get_state() == CreateKhatm.choosing_commitment_total.state

        # 6. From choosing_commitment_total (Salawat) -> entering_creator_contact
        state = DummyState(
            data={"category_group": KhatmCategoryGroup.SALAWAT.value},
            state=CreateKhatm.choosing_commitment_total.state,
        )
        await previous_wizard_step(cb, state)
        assert await state.get_state() == CreateKhatm.entering_creator_contact.state

        # 7. From entering_creator_contact -> entering_welcome
        state = DummyState(data={}, state=CreateKhatm.entering_creator_contact.state)
        await previous_wizard_step(cb, state)
        assert await state.get_state() == CreateKhatm.entering_welcome.state

        # 8. From entering_welcome -> entering_niyyat
        state = DummyState(data={}, state=CreateKhatm.entering_welcome.state)
        await previous_wizard_step(cb, state)
        assert await state.get_state() == CreateKhatm.entering_niyyat.state

        # 9. From entering_niyyat -> choosing_mode
        state = DummyState(
            data={"template_type": KhatmTemplateType.QURAN_PAGE.value},
            state=CreateKhatm.entering_niyyat.state,
        )
        await previous_wizard_step(cb, state)
        assert await state.get_state() == CreateKhatm.choosing_mode.state

        # 10. From choosing_mode (Quran) -> choosing_template
        state = DummyState(
            data={"template_type": KhatmTemplateType.QURAN_PAGE.value},
            state=CreateKhatm.choosing_mode.state,
        )
        await previous_wizard_step(cb, state)
        assert await state.get_state() == CreateKhatm.choosing_template.state

        # 11. From choosing_mode (Khutbah) -> choosing_category
        state = DummyState(
            data={"category_group": KhatmCategoryGroup.KHUTBAH.value},
            state=CreateKhatm.choosing_mode.state,
        )
        with patch("khatmsaz.bot.handlers.create_khatm.category_service.list_active", AsyncMock(return_value=[])):
            await previous_wizard_step(cb, state)
            assert await state.get_state() == CreateKhatm.choosing_category.state

        # 12. From choosing_category -> choosing_template
        state = DummyState(data={}, state=CreateKhatm.choosing_category.state)
        await previous_wizard_step(cb, state)
        assert await state.get_state() == CreateKhatm.choosing_template.state

        # 13. From choosing_template -> cancels wizard & clears state
        state = DummyState(data={}, state=CreateKhatm.choosing_template.state)
        await previous_wizard_step(cb, state)
        assert await state.get_state() is None
        cb.message.answer.assert_called()


def test_khutbah_button_in_template_keyboard():
    """Verify that template_choice_keyboard includes Khutbah option."""
    from khatmsaz.bot.keyboards import template_choice_keyboard
    kb = template_choice_keyboard("fa")
    button_datas = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    button_texts = [btn.text for row in kb.inline_keyboard for btn in row]

    assert "ck:group:KHUTBAH" in button_datas
    assert any("خطبه" in txt for txt in button_texts)
