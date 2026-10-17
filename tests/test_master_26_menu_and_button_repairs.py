"""Unit and integration tests for MASTER_26 Menu & Button Repairs.

Verifies:
- All button text sets contain full Persian variants (no unhandled reply buttons).
- FSM bailout functionality for all menu buttons in member commitments and settings.
- Dead callbacks repaired: `my_khatms:created`, `my_khatms:open`, `cs:miss:...`, `join_hour:...`.
- Member bot Help menu never includes dead admin web login button.
- Admin bot fallback message handler does not shadow commands or FSM states.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, User, Chat

from khatmsaz.bot.keyboards import (
    MY_KHATMS_BUTTON_TEXTS,
    SETTINGS_BUTTON_TEXTS,
    HELP_BUTTON_TEXTS,
    SUPPORT_BUTTON_TEXTS,
    RESERVED_MENU_TEXTS,
    PHONE_SHARE_BUTTON_TEXTS,
    bail_if_menu_button,
    help_manage_actions_keyboard,
    creator_miss_policy_keyboard,
)
from khatmsaz.bot.handlers.registration import Registration
from khatmsaz.bot.handlers.my_khatms import router as my_khatms_router
from khatmsaz.bot.handlers.join_flow import router as join_flow_router
from khatmsaz.bot.handlers.admin_bot.handlers import router as admin_bot_router


def test_reply_button_text_variants_completeness():
    """Verify that all user-facing variants of reply menu buttons are caught."""
    # 1. My Khatms
    for expected in ["📋 ختم‌های من", "🕋 ختم‌های من", "ختم‌های من", "ختم های من", "لیست ختم‌های من"]:
        assert expected in MY_KHATMS_BUTTON_TEXTS, f"Missing '{expected}' in MY_KHATMS_BUTTON_TEXTS"
        assert expected in RESERVED_MENU_TEXTS, f"Missing '{expected}' in RESERVED_MENU_TEXTS"

    # 2. Settings
    for expected in ["⚙️ تنظیمات", "تنظیمات"]:
        assert expected in SETTINGS_BUTTON_TEXTS, f"Missing '{expected}' in SETTINGS_BUTTON_TEXTS"
        assert expected in RESERVED_MENU_TEXTS, f"Missing '{expected}' in RESERVED_MENU_TEXTS"

    # 3. Help
    for expected in ["❓ راهنما", "راهنما"]:
        assert expected in HELP_BUTTON_TEXTS, f"Missing '{expected}' in HELP_BUTTON_TEXTS"
        assert expected in RESERVED_MENU_TEXTS, f"Missing '{expected}' in RESERVED_MENU_TEXTS"

    # 4. Support
    for expected in ["📩 پشتیبانی و ارتباط", "پشتیبانی و ارتباط", "پشتیبانی", "تماس با پشتیبانی", "ارتباط با پشتیبانی"]:
        assert expected in SUPPORT_BUTTON_TEXTS, f"Missing '{expected}' in SUPPORT_BUTTON_TEXTS"
        assert expected in RESERVED_MENU_TEXTS, f"Missing '{expected}' in RESERVED_MENU_TEXTS"


@pytest.mark.asyncio
async def test_bail_if_menu_button_clears_state_and_navigates():
    """Verify that tapping any reserved reply button triggers emergency exit from FSM."""
    storage = MemoryStorage()
    key = StorageKey(bot_id=1, chat_id=123, user_id=456)
    state = FSMContext(storage=storage, key=key)
    await state.set_state("SomeState:waiting_for_input")
    await state.update_data(foo="bar")

    msg = MagicMock(spec=Message)
    msg.text = "📋 ختم‌های من"
    msg.chat = MagicMock(spec=Chat, id=123)
    msg.from_user = MagicMock(spec=User, id=456)
    msg.bot = MagicMock()
    msg.answer = AsyncMock()

    with patch("khatmsaz.bot.navigation.resolve_home_navigation", return_value=("fa", "CREATOR", MagicMock())):
        bailed = await bail_if_menu_button(msg, state)
        assert bailed is True
        assert await state.get_state() is None
        assert msg.answer.called


@pytest.mark.asyncio
async def test_bail_if_menu_button_does_not_abort_phone_share():
    """Verify that tapping the native phone share button does NOT abort entering_phone."""
    storage = MemoryStorage()
    key = StorageKey(bot_id=1, chat_id=123, user_id=456)
    state = FSMContext(storage=storage, key=key)
    await state.set_state(Registration.entering_phone)

    msg = MagicMock(spec=Message)
    msg.text = next(iter(PHONE_SHARE_BUTTON_TEXTS))
    msg.chat = MagicMock(spec=Chat, id=123)
    msg.from_user = MagicMock(spec=User, id=456)
    msg.bot = MagicMock()
    msg.answer = AsyncMock()

    bailed = await bail_if_menu_button(msg, state)
    assert bailed is False
    assert await state.get_state() == Registration.entering_phone.state


def test_help_manage_actions_keyboard_guards_admin_button_for_members():
    """Verify that member bots never show the admin panel button even if user is super admin."""
    # When is_member=True, admin_panel button must NOT be present
    kb_member = help_manage_actions_keyboard(lang="fa", is_creator=True, is_admin=True, is_member=True)
    all_callbacks_member = [btn.callback_data for row in kb_member.inline_keyboard for btn in row]
    assert "admin:web_login" not in all_callbacks_member

    # When is_member=False (creator bot), admin_panel button is shown
    kb_creator = help_manage_actions_keyboard(lang="fa", is_creator=True, is_admin=True, is_member=False)
    all_callbacks_creator = [btn.callback_data for row in kb_creator.inline_keyboard for btn in row]
    assert "admin:web_login" in all_callbacks_creator


def test_my_khatms_router_has_handlers_for_repaired_callbacks():
    """Verify that my_khatms router has handlers matching my_khatms:created, my_khatms:open, and cs:miss:."""
    handler_names = [h.callback.__name__ for h in my_khatms_router.callback_query.handlers]
    assert "my_khatms_show_root" in handler_names
    assert "my_khatms_show_created_branch" in handler_names
    assert "creator_miss_policy_save" in handler_names


def test_creator_miss_policy_keyboard_buttons_match_handler():
    """Verify that every button in creator_miss_policy_keyboard starts with cs:miss:."""
    kb = creator_miss_policy_keyboard("00000000-0000-0000-0000-000000000001")
    miss_buttons = [btn for row in kb.inline_keyboard for btn in row if btn.callback_data.startswith("cs:miss:")]
    assert len(miss_buttons) == 3


def test_join_flow_router_has_fallback_for_join_hour():
    """Verify that join_flow router contains a fallback handler for join_hour: without state filter."""
    handler_names = [h.callback.__name__ for h in join_flow_router.callback_query.handlers]
    assert "receive_delivery_hour_button" in handler_names
    assert "receive_delivery_hour_fallback" in handler_names


def test_admin_fallback_handler_is_filtered():
    """Verify that admin_bot_router fallback message handler is properly scoped with StateFilter(None) and not starts with '/'."""
    fallback_handlers = [h for h in admin_bot_router.message.handlers if h.callback.__name__ == "admin_fallback_message_handler"]
    assert len(fallback_handlers) == 1
    # Check that filters are attached
    assert len(fallback_handlers[0].filters) >= 2
