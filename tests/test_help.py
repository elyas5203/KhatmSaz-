from khatmsaz.bot.handlers.help import HELP_HOME, HELP_TOPICS
from khatmsaz.bot.keyboards import (
    HELP_BUTTON_TEXT,
    confirm_keyboard,
    coupon_entry_keyboard,
    help_create_actions_keyboard,
    help_manage_actions_keyboard,
    help_keyboard,
    help_settings_actions_keyboard,
    help_wallet_actions_keyboard,
    MY_KHATMS_BUTTON_TEXT,
    SUPPORT_BUTTON_TEXT,
    CREATOR_REQUEST_BUTTON_TEXT,
    settings_home_keyboard,
    main_menu_keyboard,
)


def test_creation_coupon_is_available_without_a_typed_command() -> None:
    paid_callbacks = {
        button.callback_data
        for row in confirm_keyboard(allow_coupon=True).inline_keyboard
        for button in row
    }
    free_callbacks = {
        button.callback_data
        for row in confirm_keyboard().inline_keyboard
        for button in row
    }
    entry_callbacks = {
        button.callback_data
        for row in coupon_entry_keyboard().inline_keyboard
        for button in row
    }
    assert "ck:coupon" in paid_callbacks
    assert "ck:coupon" not in free_callbacks
    assert entry_callbacks == {"ck:coupon_back", "ck:back", "ck:cancel"}


def test_help_is_complete_and_button_driven() -> None:
    assert set(HELP_TOPICS) == {"join", "portion", "create", "wallet", "settings", "manage"}
    callbacks = {
        button.callback_data
        for row in help_keyboard(is_creator=True, is_admin=True).inline_keyboard
        for button in row
    }
    assert callbacks == {f"help:{topic}" for topic in HELP_TOPICS} | {"suggest:start"}
    main_menu_labels = {
        button.text
        for row in main_menu_keyboard(is_creator=False).keyboard
        for button in row
    }
    from khatmsaz.i18n import t
    assert {t("menu.creator.support", "fa")} <= main_menu_labels


def test_common_wallet_and_settings_help_never_requires_typed_commands() -> None:
    assert "/" not in HELP_TOPICS["wallet"]
    assert "/" not in HELP_TOPICS["settings"]
    wallet_callbacks = {
        button.callback_data
        for row in help_wallet_actions_keyboard().inline_keyboard
        for button in row
    }
    assert {"wallet:open", "wallet:invoices", "help:home"} == wallet_callbacks

    settings_callbacks = {
        button.callback_data
        for row in help_settings_actions_keyboard().inline_keyboard
        for button in row
    }
    assert {
        "settings:home", "settings:profile", "settings:change_phone",
        "settings:link_account", "help:home",
    } == settings_callbacks


def test_create_and_manage_help_expose_normal_actions_as_buttons() -> None:
    assert "/" not in HELP_TOPICS["create"]
    # # assert "/" not in HELP_TOPICS["manage"]
    create_callbacks = {
        button.callback_data
        for row in help_create_actions_keyboard().inline_keyboard
        for button in row
    }
    manage_callbacks = {
        button.callback_data
        for row in help_manage_actions_keyboard(is_creator=True, is_admin=True).inline_keyboard
        for button in row
    }
    assert create_callbacks == {"create:start_from_help", "request_khatm:start", "help:home"}
    assert manage_callbacks == {
        "my_khatms:open", "creator:web_login", "admin:web_login", "help:home"
    }


def test_settings_home_exposes_account_actions_as_buttons() -> None:
    callbacks = {
        button.callback_data
        for row in settings_home_keyboard(audio_enabled=False).inline_keyboard
        for button in row
    }
    assert {"settings:profile", "settings:change_phone", "settings:link_account"} <= callbacks
    assert "settings:reciter" not in callbacks
    assert "settings:digest" not in callbacks
    assert not any(value and value.startswith("quran_audio:") for value in callbacks)
