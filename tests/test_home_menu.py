from khatmsaz.i18n import t
from khatmsaz.bot.keyboards import (
    CREATE_BUTTON_TEXT,
    HELP_BUTTON_TEXT,
    MY_KHATMS_BUTTON_TEXT,
    REPORT_BUTTON_TEXT,
    SETTINGS_BUTTON_TEXT,
    TODAY_BUTTON_TEXT,
    RESERVED_MENU_TEXTS,
    participant_menu_keyboard,
    creator_menu_keyboard,
    main_menu_keyboard,
)
from khatmsaz.bot.navigation import home_markup_for_role
from khatmsaz.modules.identity.models import UserRole


def test_creator_home_menu_leads_with_create_not_today():
    # Owner (2026-09-28): the creator bot is only for building khatms — creators
    # don't receive portions here — so the top button is «ساخت ختم جدید», not «امروز».
    labels = [button.text for row in main_menu_keyboard(is_creator=True).keyboard for button in row]
    assert labels == [
        t("menu.create", "fa"),
        t("menu.creator.management", "fa"),
        t("menu.creator.finance", "fa"),
        t("menu.settings", "fa"),
        t("menu.creator.support", "fa"),
    ]
    assert t("menu.today", "fa") not in labels


def test_creator_bot_menu_is_fixed_for_every_role():
    creator_labels = [
        button.text for row in creator_menu_keyboard("fa").keyboard for button in row
    ]
    for role in UserRole:
        role_labels = [
            button.text
            for row in home_markup_for_role("fa", role).keyboard
            for button in row
        ]
        assert role_labels == creator_labels
        assert t("help.button.admin_panel", "fa") not in role_labels


def test_participant_menu_exactly_matches_dec_py_0076():
    labels = [button.text for row in participant_menu_keyboard("fa").keyboard for button in row]
    assert labels == [
        t("menu.today", "fa"),
        t("menu.public_khatms", "fa"),
        t("menu.settings", "fa"), t("menu.support", "fa"),
    ]


def test_every_emitted_navigation_reply_label_is_reserved_in_every_language():
    for lang in ("fa", "ar", "en"):
        keyboards = [participant_menu_keyboard(lang), creator_menu_keyboard(lang)]
        from khatmsaz.bot.keyboards import (
            creator_finance_keyboard, creator_management_keyboard, creator_support_keyboard,
        )
        keyboards.extend([
            creator_management_keyboard(lang), creator_finance_keyboard(lang), creator_support_keyboard(lang),
        ])
        labels = {button.text for keyboard in keyboards for row in keyboard.keyboard for button in row}
        assert labels <= RESERVED_MENU_TEXTS
        assert t("registration.share_phone", lang) in RESERVED_MENU_TEXTS


def test_visibility_keyboard_contains_all_three_modes():
    from khatmsaz.bot.keyboards import visibility_choice_keyboard

    callbacks = [
        button.callback_data
        for row in visibility_choice_keyboard().inline_keyboard
        for button in row
    ]
    # The three visibility modes, plus a cancel row now added to every wizard
    # step (goal: «انصراف» available at every step).
    assert callbacks == [
        "ck:visibility:PUBLIC",
        "ck:visibility:UNLISTED",
        "ck:visibility:PRIVATE",
        "ck:cancel",
    ]


def test_creator_settings_are_button_driven_and_scope_sensitive():
    from khatmsaz.bot.keyboards import creator_settings_keyboard

    quran_callbacks = {
        button.callback_data
        for row in creator_settings_keyboard(
            "khatm-id", is_quran=True, is_commitment=True,
            is_open=False,
            allow_skip_today=True, allow_pause=False, allow_snooze=True,
            miss_threshold=2, miss_window_days=7,
            content_mode="AUTO",
        ).inline_keyboard
        for button in row
    }
    open_salawat_callbacks = {
        button.callback_data
        for row in creator_settings_keyboard(
            "khatm-id", is_quran=False, is_commitment=False,
            is_open=True,
            allow_skip_today=False, allow_pause=False, allow_snooze=False,
            miss_threshold=2, miss_window_days=7,
            content_mode="AUTO",
        ).inline_keyboard
        for button in row
    }
    # cs:skip and cs:misses were removed with the emergency-portion/
    # backup-reader feature (owner decision, 2026-09-21) — no longer
    # offered to creators.
    assert {
        "cs:modes:khatm-id", "cs:pause:khatm-id", "cs:snooze:khatm-id",
    } <= quran_callbacks
    assert "cs:skip:khatm-id" not in quran_callbacks
    assert "cs:misses:khatm-id" not in quran_callbacks
    assert open_salawat_callbacks == {
        "cs:edit:khatm-id:title", "cs:edit:khatm-id:welcome",
        "cs:end:khatm-id", "cs:end_clear:khatm-id", "cs:schedule:khatm-id",
        "my_khatms:open"
    }


def test_open_schedule_menu_exposes_simple_presets_and_specific_date():
    from khatmsaz.bot.keyboards import creator_schedule_keyboard

    buttons = [
        button
        for row in creator_schedule_keyboard("khatm-id").inline_keyboard
        for button in row
    ]
    callbacks = {button.callback_data for button in buttons}
    labels = {button.text for button in buttons}
    assert {
        "cs:schedule_set:khatm-id:off",
        "cs:schedule_set:khatm-id:daily",
        "cs:schedule_set:khatm-id:weekly:0,1,2,3,4",
        "cs:schedule_set:khatm-id:weekly:5,6",
        "cs:schedule_set:khatm-id:every:3",
        "cs:schedule_date:khatm-id",
    } <= callbacks
    assert any(label.endswith("روزهای کاری") for label in labels)
    assert any(label.endswith("آخرهفته") for label in labels)
    assert any(label.endswith("یک تاریخ مشخص") for label in labels)
