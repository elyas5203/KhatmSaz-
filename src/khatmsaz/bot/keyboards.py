"""Shared reply/inline keyboards. Kept in one place so the Home menu stays
intentionally shallow (DOMAIN_MODEL.md §4) — a new button here is a product
decision, not just a UI tweak.
"""

from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from khatmsaz.modules.khatm.quran_editions import QURAN_CREATION_EDITION_IDS, QURAN_EDITIONS
from khatmsaz.i18n import t, variants

# These stay the Persian text by default so every existing `message.answer(f"...{CREATE_BUTTON_TEXT}...")`
# reference (there are several, outside the F.text filters) keeps working
# unchanged. For matching a *received* button press regardless of the
# user's language, use the `*_BUTTON_TEXTS` frozensets below instead — see
# `khatmsaz.i18n`'s module docstring for why a plain `==` filter can't do
# this once a button's label is language-dependent.
CREATE_BUTTON_TEXT = t("menu.create", "fa")
MY_KHATMS_BUTTON_TEXT = t("menu.my_khatms", "fa")
TODAY_BUTTON_TEXT = t("menu.today", "fa")
REPORT_BUTTON_TEXT = t("menu.report", "fa")
SETTINGS_BUTTON_TEXT = t("menu.settings", "fa")
HELP_BUTTON_TEXT = t("menu.help", "fa")

PUBLIC_KHATMS_BUTTON_TEXT = t("menu.public_khatms", "fa")
SUPPORT_BUTTON_TEXT = t("menu.support", "fa")
CREATOR_REQUEST_BUTTON_TEXT = t("menu.creator_request", "fa")

CREATE_BUTTON_TEXTS = variants("menu.create")
MY_KHATMS_BUTTON_TEXTS = variants("menu.my_khatms")
TODAY_BUTTON_TEXTS = variants("menu.today")
REPORT_BUTTON_TEXTS = variants("menu.report")
SETTINGS_BUTTON_TEXTS = variants("menu.settings")
HELP_BUTTON_TEXTS = variants("menu.help")
PUBLIC_KHATMS_BUTTON_TEXTS = variants("menu.public_khatms")
SUPPORT_BUTTON_TEXTS = variants("menu.support")
CREATOR_REQUEST_BUTTON_TEXTS = variants("menu.creator_request")
CREATOR_MANAGEMENT_BUTTON_TEXTS = variants("menu.creator.management")
CREATOR_FINANCE_BUTTON_TEXTS = variants("menu.creator.finance")
CREATOR_SUPPORT_BUTTON_TEXTS = variants("menu.creator.support")
BACK_TO_MAIN_BUTTON_TEXTS = variants("menu.back_to_main")
PHONE_SHARE_BUTTON_TEXTS = variants("registration.share_phone")

# Every free-text step inside a wizard/FSM state (title, niyyat, target,
# contribution amount...) must check incoming text against this set first.
# Without it, pressing a menu button *while* a wizard is waiting for text
# gets silently swallowed as that wizard's answer instead of navigating —
# this actually happened in testing (a khatm literally titled "🕋 ختم‌های من").
# Includes every language's variant of every button (see i18n note above).
RESERVED_MENU_TEXTS = (
    CREATE_BUTTON_TEXTS | MY_KHATMS_BUTTON_TEXTS | TODAY_BUTTON_TEXTS
    | REPORT_BUTTON_TEXTS | SETTINGS_BUTTON_TEXTS | HELP_BUTTON_TEXTS
    | PUBLIC_KHATMS_BUTTON_TEXTS | SUPPORT_BUTTON_TEXTS | CREATOR_REQUEST_BUTTON_TEXTS
    | CREATOR_MANAGEMENT_BUTTON_TEXTS | CREATOR_FINANCE_BUTTON_TEXTS
    | CREATOR_SUPPORT_BUTTON_TEXTS | BACK_TO_MAIN_BUTTON_TEXTS | PHONE_SHARE_BUTTON_TEXTS
    | {"📢 ارسال پیام گروهی"}
)

def member_menu_keyboard(lang: str = "fa") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("menu.today", lang))],
            [KeyboardButton(text=t("menu.my_khatms", lang))],
            [KeyboardButton(text=t("menu.public_khatms", lang))],
            [KeyboardButton(text=t("menu.settings", lang)), KeyboardButton(text=t("menu.support", lang))],
        ],
        resize_keyboard=True,
    )

def is_member_bot(bot) -> bool:
    """True when this Bot instance is a category-specific MEMBER bot.

    `khatmsaz_role` holds a `BotRole` enum (a `str, Enum`), so `str(role)`
    yields ``'BotRole.MEMBER'`` — never the bare ``'MEMBER'``. Compare the
    enum value instead; this also tolerates a plain string being stored.
    """
    role = getattr(bot, "khatmsaz_role", None)
    if role is None:
        return False
    return getattr(role, "value", role) == "MEMBER"


def home_keyboard_for_bot(bot, lang: str) -> ReplyKeyboardMarkup:
    """Return the correct home keyboard based on whether bot is MEMBER or CREATOR.
    Always use this instead of bare main_menu_keyboard() in shared handlers."""
    if is_member_bot(bot):
        return member_menu_keyboard(lang)
    return main_menu_keyboard(lang)


def participant_menu_keyboard(lang: str = "fa") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("menu.today", lang))],
            [KeyboardButton(text=t("menu.public_khatms", lang))],
            [KeyboardButton(text=t("menu.settings", lang)), KeyboardButton(text=t("menu.support", lang))],
        ],
        resize_keyboard=True,
    )

def support_inline_keyboard(lang: str = "fa", is_participant: bool = False, is_admin: bool = False, is_creator: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=t("support.button.send_message", lang), callback_data="suggest:start")]
    ]
    if not is_participant and not is_creator and not is_admin:
        buttons.append([InlineKeyboardButton(text=t("menu.creator_request", lang), callback_data="creator_request:start")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def back_to_support_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("button.back", lang), callback_data="support:menu")]
        ]
    )



def creator_menu_keyboard(lang: str = "fa") -> ReplyKeyboardMarkup:
    # Owner (2026-09-28): the creator bot is ONLY for building khatms — a creator
    # never receives their own portions here (they join member bots to take part).
    # So the top button is «➕ ساخت ختم جدید» (handy, front-and-centre) instead of
    # «امروز», which belonged to the participation flow that doesn't apply here.
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("menu.create", lang))],
            [KeyboardButton(text=t("menu.creator.management", lang))],
            [KeyboardButton(text=t("menu.creator.finance", lang))],
            [KeyboardButton(text=t("menu.settings", lang)), KeyboardButton(text=t("menu.creator.support", lang))],
        ],
        resize_keyboard=True,
    )

def creator_management_keyboard(lang: str = "fa") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("menu.create", lang)), KeyboardButton(text=t("menu.my_khatms", lang))],
            [KeyboardButton(text="📢 ارسال پیام گروهی")],
            [KeyboardButton(text=t("menu.back_to_main", lang))],
        ],
        resize_keyboard=True,
    )

def creator_finance_keyboard(lang: str = "fa") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("menu.report", lang))],
            # Add wallet button later if needed
            [KeyboardButton(text=t("menu.back_to_main", lang))],
        ],
        resize_keyboard=True,
    )

def creator_support_keyboard(lang: str = "fa") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("menu.help", lang)), KeyboardButton(text=t("menu.support", lang))],
            [KeyboardButton(text=t("menu.back_to_main", lang))],
        ],
        resize_keyboard=True,
    )

def admin_menu_keyboard(lang: str = "fa") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            # A normal chat button first opens the admin panel message.  The
            # Mini App is then launched from its signed inline button, so the
            # user always gets a recoverable entry instruction in chat.
            [KeyboardButton(text=t("help.button.admin_panel", lang))],
            [KeyboardButton(text=t("menu.settings", lang))],
        ],
        resize_keyboard=True,
    )

def main_menu_keyboard(lang: str = "fa", is_creator: bool = False, is_admin: bool = False) -> ReplyKeyboardMarkup:
    if is_admin:
        return admin_menu_keyboard(lang)
    if is_creator:
        return creator_menu_keyboard(lang)
    return participant_menu_keyboard(lang)


def language_choice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="فارسی", callback_data="first_lang:fa"),
                InlineKeyboardButton(text="العربية", callback_data="first_lang:ar"),
                InlineKeyboardButton(text="English", callback_data="first_lang:en"),
            ]
        ]
    )


def content_preferences_keyboard(*, audio_enabled: bool) -> InlineKeyboardMarkup:
    audio_text = "🔇 خاموش کردن صوت" if audio_enabled else "🔊 روشن کردن صوت قرآن"
    audio_value = "off" if audio_enabled else "on"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=audio_text, callback_data=f"quran_audio:{audio_value}")],
            [InlineKeyboardButton(text="📖 راهنمای سهم قرآن", callback_data="quran_help")],
            [InlineKeyboardButton(text="❓ راهنمای کامل بات", callback_data="help:home")],
        ]
    )


def settings_home_keyboard(*, audio_enabled: bool, lang: str = "fa") -> InlineKeyboardMarkup:
    """Every personal setting reachable by tapping — no slash command is
    required for any of these (user request, 2026-09-18): the old screen
    listed `/language`, `/timezone`, `/font`, etc. as text to type, which
    contradicts the project's "click, don't type" principle."""
    audio_text = t("settings.button.audio_off", lang) if audio_enabled else t("settings.button.audio_on", lang)
    audio_value = "off" if audio_enabled else "on"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=audio_text, callback_data=f"quran_audio:{audio_value}")],
            [
                InlineKeyboardButton(text=t("settings.button.language", lang), callback_data="settings:language"),
                InlineKeyboardButton(text=t("settings.button.reciter", lang), callback_data="settings:reciter"),
                # InlineKeyboardButton(text=t("settings.button.font", lang), callback_data="settings:font"),
                # InlineKeyboardButton(text=t("settings.button.content", lang), callback_data="settings:content"),
            ],
            [
                InlineKeyboardButton(text=t("settings.button.reminder", lang), callback_data="settings:reminder"),
                InlineKeyboardButton(text=t("settings.button.digest", lang), callback_data="settings:digest"),
            ],
            [
                InlineKeyboardButton(text=t("settings.button.sms_menu", lang), callback_data="settings:sms"),
                InlineKeyboardButton(text=t("settings.button.timezone", lang), callback_data="settings:timezone"),
            ],
            [InlineKeyboardButton(text=t("settings.button.profile", lang), callback_data="settings:profile")],
            [
                InlineKeyboardButton(text=t("settings.button.change_phone", lang), callback_data="settings:change_phone"),
                InlineKeyboardButton(text=t("settings.button.link_account", lang), callback_data="settings:link_account"),
            ],
        ]
    )


def settings_back_row(lang: str = "fa") -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(text=t("settings.button.back", lang), callback_data="settings:home")]


def settings_language_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="فارسی", callback_data="set_language:fa"),
                InlineKeyboardButton(text="العربية", callback_data="set_language:ar"),
                InlineKeyboardButton(text="English", callback_data="set_language:en"),
            ],
            settings_back_row(lang),
        ]
    )


def settings_font_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("settings.button.font_normal", lang), callback_data="set_font:normal"),
                InlineKeyboardButton(text=t("settings.button.font_large", lang), callback_data="set_font:large"),
            ],
            settings_back_row(lang),
        ]
    )


def settings_reciter_keyboard(reciters: list[tuple[str, str]], lang: str = "fa") -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=name, callback_data=f"set_reciter:{key}")] for key, name in reciters]
    rows.append(settings_back_row(lang))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def settings_content_keyboard(*, translation_enabled: bool, tafsir_enabled: bool, lang: str = "fa") -> InlineKeyboardMarkup:
    def _label(key: str, enabled: bool) -> str:
        toggle = t("settings.button.turn_off", lang) if enabled else t("settings.button.turn_on", lang)
        return f"{t(key, lang)}: {toggle}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_label("settings.label.translation", translation_enabled),
                    callback_data=f"set_content:translation:{'off' if translation_enabled else 'on'}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=_label("settings.label.tafsir", tafsir_enabled),
                    callback_data=f"set_content:tafsir:{'off' if tafsir_enabled else 'on'}",
                )
            ],
            settings_back_row(lang),
        ]
    )


_REMINDER_HOURS = [7, 8, 9, 10, 12, 14, 16, 18, 20, 22]


def settings_reminder_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    hour_buttons = [InlineKeyboardButton(text=f"{h}:۰۰", callback_data=f"set_reminder:{h}") for h in _REMINDER_HOURS]
    rows = [hour_buttons[i : i + 5] for i in range(0, len(hour_buttons), 5)]
    rows.append([InlineKeyboardButton(text=t("settings.button.reminder_off", lang), callback_data="set_reminder:off")])
    rows.append(settings_back_row(lang))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def settings_on_off_keyboard(*, prefix: str, enabled: bool, lang: str = "fa") -> InlineKeyboardMarkup:
    on_text = t("settings.button.on_active", lang) if enabled else t("settings.button.turn_on", lang)
    off_text = t("settings.button.turn_off", lang) if enabled else t("settings.button.off_active", lang)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=on_text, callback_data=f"{prefix}:on"),
                InlineKeyboardButton(text=off_text, callback_data=f"{prefix}:off"),
            ],
            settings_back_row(lang),
        ]
    )


def sms_subscription_keyboard(options, *, active: bool, lang: str = "fa") -> InlineKeyboardMarkup:
    """Owner request (2026-09-20): SMS reminders need a paid, time-limited
    subscription — this replaces a plain on/off toggle with plan-purchase
    buttons. `options` is a list of `SmsPlanOption` (months, price_toman)."""
    rows = [
        [InlineKeyboardButton(
            text=t("settings.button.sms_buy", lang, months=option.months, price=f"{option.price_toman:,}"),
            callback_data=f"sms_buy:{option.months}",
        )]
        for option in options
    ]
    if active:
        rows.append([InlineKeyboardButton(text=t("settings.button.sms_off", lang), callback_data="set_sms:off")])
    rows.append(settings_back_row(lang))
    return InlineKeyboardMarkup(inline_keyboard=rows)


_TIMEZONE_CHOICES = [
    ("تهران", "Asia/Tehran"),
    ("دبی", "Asia/Dubai"),
    ("استانبول", "Europe/Istanbul"),
    ("لندن", "Europe/London"),
    ("برلین", "Europe/Berlin"),
    ("نیویورک", "America/New_York"),
    ("کوالالامپور", "Asia/Kuala_Lumpur"),
    ("سیدنی", "Australia/Sydney"),
]


def settings_timezone_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"set_timezone:{tz}")]
        for label, tz in _TIMEZONE_CHOICES
    ]
    rows.append(settings_back_row(lang))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def help_keyboard(lang: str = "fa", is_creator: bool = False, is_admin: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=t("help.button.join", lang), callback_data="help:join"),
            InlineKeyboardButton(text=t("help.button.portion", lang), callback_data="help:portion"),
        ],
    ]
    if is_creator or is_admin:
        buttons.append([
            InlineKeyboardButton(text=t("help.button.create", lang), callback_data="help:create"),
            InlineKeyboardButton(text=t("help.button.wallet", lang), callback_data="help:wallet"),
        ])
        buttons.append([
            InlineKeyboardButton(text=t("help.button.settings", lang), callback_data="help:settings"),
            InlineKeyboardButton(text=t("help.button.manage", lang), callback_data="help:manage"),
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text=t("help.button.settings", lang), callback_data="help:settings"),
        ])
        
    buttons.append([InlineKeyboardButton(text=t("suggestions.button.open", lang), callback_data="suggest:start")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def help_wallet_actions_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("help.button.balance", lang), callback_data="wallet:open")],
            [InlineKeyboardButton(text=t("help.button.invoices", lang), callback_data="wallet:invoices")],
            [InlineKeyboardButton(text=t("help.button.back", lang), callback_data="help:home")],
        ]
    )


def help_settings_actions_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("help.button.open_settings", lang), callback_data="settings:home")],
            [
                InlineKeyboardButton(text=t("help.button.edit_profile", lang), callback_data="settings:profile"),
                InlineKeyboardButton(text=t("help.button.change_phone", lang), callback_data="settings:change_phone"),
            ],
            [InlineKeyboardButton(text=t("help.button.link_account", lang), callback_data="settings:link_account")],
            [InlineKeyboardButton(text=t("help.button.back", lang), callback_data="help:home")],
        ]
    )


def help_create_actions_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("help.button.start_create", lang), callback_data="create:start_from_help")],
            [InlineKeyboardButton(text=t("help.button.request_type", lang), callback_data="request_khatm:start")],
            [InlineKeyboardButton(text=t("help.button.back", lang), callback_data="help:home")],
        ]
    )


def help_manage_actions_keyboard(lang: str = "fa", is_creator: bool = False, is_admin: bool = False) -> InlineKeyboardMarkup:
    buttons = []
    if is_creator or is_admin:
        buttons.append([InlineKeyboardButton(text=t("help.button.my_khatms", lang), callback_data="my_khatms:open")])
        buttons.append([InlineKeyboardButton(text=t("help.button.creator_panel", lang), callback_data="creator:web_login")])
    if is_admin:
        buttons.append([InlineKeyboardButton(text=t("help.button.admin_panel", lang), callback_data="admin:web_login")])
    buttons.append([InlineKeyboardButton(text=t("help.button.back", lang), callback_data="help:home")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _ck_cancel_row(lang: str) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(text=t("ck.cancel", lang), callback_data="ck:cancel")]


def commitment_mode_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("ck.mode.commitment", lang), callback_data="ck:mode:COMMITMENT")],
            [InlineKeyboardButton(text=t("ck.mode.open", lang), callback_data="ck:mode:OPEN")],
            _ck_cancel_row(lang),
        ]
    )


def template_choice_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("ck.tpl.quran", lang), callback_data="ck:tpl:QURAN_PAGE")],
            [InlineKeyboardButton(text=t("ck.tpl.salawat", lang), callback_data="ck:group:SALAWAT")],
            [InlineKeyboardButton(text=t("ck.tpl.dua", lang), callback_data="ck:group:DUA")],
            [InlineKeyboardButton(text=t("ck.tpl.laan", lang), callback_data="ck:group:LAAN")],
            _ck_cancel_row(lang),
        ]
    )


_CATEGORY_GROUP_EMOJI = {"SALAWAT": "📿", "LAAN": "🗡", "DUA": "🤲"}


def category_choice_keyboard(
    categories: list, *, group: str, allow_custom_request: bool = False, lang: str = "fa"
) -> InlineKeyboardMarkup:
    """Show only children of one explicit top-level devotional family."""
    rows = [
        [InlineKeyboardButton(
            text=f"{_CATEGORY_GROUP_EMOJI.get(category.group.value, '•')} {category.title}",
            callback_data=f"ck:cat:{category.id}",
        )]
        for category in categories
    ]
    if allow_custom_request:
        rows.append([InlineKeyboardButton(text=t("ck.cat.custom", lang), callback_data="ck:cat:custom")])
    rows.append(_ck_cancel_row(lang))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def skip_niyyat_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("ck.skip_niyyat", lang), callback_data="ck:skip_niyyat")],
            _ck_cancel_row(lang),
        ]
    )


def edition_choice_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=info["label"], callback_data=f"ck:edition:{key}")]
        for key in QURAN_CREATION_EDITION_IDS
        for info in [QURAN_EDITIONS[key]]
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def content_delivery_mode_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("ck.content_mode.auto", lang), callback_data="ck:content_mode:AUTO")],
            [InlineKeyboardButton(text=t("ck.content_mode.photo", lang), callback_data="ck:content_mode:PHOTO")],
            [InlineKeyboardButton(text=t("ck.content_mode.text", lang), callback_data="ck:content_mode:TEXT")],
            _ck_cancel_row(lang),
        ]
    )


def reminder_tone_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("ck.tone.friendly", lang), callback_data="ck:tone:FRIENDLY")],
            [InlineKeyboardButton(text=t("ck.tone.formal", lang), callback_data="ck:tone:FORMAL")],
            [InlineKeyboardButton(text=t("ck.tone.devotional", lang), callback_data="ck:tone:DEVOTIONAL")],
            [InlineKeyboardButton(text=t("ck.tone.short", lang), callback_data="ck:tone:SHORT")],
            _ck_cancel_row(lang),
        ]
    )


def creator_display_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("ck.display.full", lang), callback_data="ck:creator_display:FULL_NAME")],
            [InlineKeyboardButton(text=t("ck.display.first", lang), callback_data="ck:creator_display:FIRST_NAME")],
            [InlineKeyboardButton(text=t("ck.display.pseudonym", lang), callback_data="ck:creator_display:PSEUDONYM")],
            [InlineKeyboardButton(text=t("ck.display.anonymous", lang), callback_data="ck:creator_display:ANONYMOUS")],
            _ck_cancel_row(lang),
        ]
    )


def start_schedule_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("ck.start.now", lang), callback_data="ck:start:now")],
            [InlineKeyboardButton(text=t("ck.start.future", lang), callback_data="ck:start:future")],
            _ck_cancel_row(lang),
        ]
    )


def capacity_choice_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("ck.capacity.limited", lang), callback_data="ck:capacity:limited")],
            [InlineKeyboardButton(text=t("ck.capacity.unlimited", lang), callback_data="ck:capacity:unlimited")],
            _ck_cancel_row(lang),
        ]
    )


def visibility_choice_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("ck.visibility.public", lang), callback_data="ck:visibility:PUBLIC")],
            [InlineKeyboardButton(text=t("ck.visibility.unlisted", lang), callback_data="ck:visibility:UNLISTED")],
            [InlineKeyboardButton(text=t("ck.visibility.private", lang), callback_data="ck:visibility:PRIVATE")],
            _ck_cancel_row(lang),
        ]
    )


def public_khatms_keyboard(khatms) -> InlineKeyboardMarkup | None:
    if not khatms:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"🌱 پیوستن به «{khatm.title[:40]}»", callback_data=f"public_join:{khatm.id}")]
            for khatm in khatms
        ]
    )


def advertising_choice_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("ck.ads.on", lang), callback_data="ck:ads:ON")],
            [InlineKeyboardButton(text=t("ck.ads.off", lang), callback_data="ck:ads:OFF")],
            _ck_cancel_row(lang),
        ]
    )


def confirm_keyboard(*, allow_coupon: bool = False, lang: str = "fa") -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=t("ck.confirm", lang), callback_data="ck:confirm")]]
    if allow_coupon:
        rows.append([InlineKeyboardButton(text=t("ck.coupon", lang), callback_data="ck:coupon")])
    rows.append(_ck_cancel_row(lang))
    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )


def coupon_entry_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("ck.coupon_back", lang), callback_data="ck:coupon_back")],
            _ck_cancel_row(lang),
        ]
    )


def portion_done_keyboard(
    khatm_id: str, *, allow_skip_today: bool = False, allow_snooze: bool = True, undo_completed_id: str | None = None,
    undo_next_id: str | None = None, lang: str = "fa",
) -> InlineKeyboardMarkup:
    """For a portion that's still PENDING (not completed yet) — shows the
    content + "done" buttons. Owner-reported bug (2026-09-21): this was
    also being reused for the post-completion confirmation message, where
    "show content"/"done" make no sense anymore (the portion is already
    done) — see `post_completion_keyboard` below for that case instead.
    `allow_skip_today` is kept as a no-op parameter (the "امروز نمی‌رسم"
    button it used to add was removed with the emergency-portion system,
    BACKLOG.md §23) so callers don't need updating."""
    rows = [
        [InlineKeyboardButton(text=t("portions.button.show_content", lang), callback_data=f"content:{khatm_id}")],
        [InlineKeyboardButton(text=t("portions.button.done", lang), callback_data=f"done:{khatm_id}")],
    ]
    if allow_snooze:
        rows.append([InlineKeyboardButton(text=t("portions.button.snooze", lang), callback_data=f"snooze_ask:{khatm_id}")])
    if undo_completed_id:
        next_id = undo_next_id or "none"
        rows.append([InlineKeyboardButton(
            text=t("portions.button.undo", lang), callback_data=f"undo:{undo_completed_id}:{next_id}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def post_completion_keyboard(
    khatm_id: str, *, allow_snooze: bool = True, undo_completed_id: str | None = None,
    undo_next_id: str | None = None, lang: str = "fa",
) -> InlineKeyboardMarkup:
    """For the confirmation message right after a portion was marked done
    (`mark_portion_done`) — deliberately has no "show content"/"done"
    buttons, since there's nothing pending to show or complete anymore
    (owner-reported UX bug, 2026-09-21: the old shared keyboard kept
    showing those two buttons even after completion, which was confusing)."""
    rows = []
    if allow_snooze:
        rows.append([InlineKeyboardButton(text=t("portions.button.snooze", lang), callback_data=f"snooze_ask:{khatm_id}")])
    if undo_completed_id:
        next_id = undo_next_id or "none"
        rows.append([InlineKeyboardButton(
            text=t("portions.button.undo", lang), callback_data=f"undo:{undo_completed_id}:{next_id}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def delivery_hour_keyboard(callback_prefix: str, lang: str = "fa") -> InlineKeyboardMarkup:
    """Owner request (2026-09-22, put-yourself-in-a-confused-user's-shoes
    pass): asking someone to type a raw 0-23 hour was real friction for
    anyone unsure about 24-hour clock notation. Plain-language time-of-day
    buttons cover the common cases without typing; the caller's own typed-
    number handler stays as a fallback for anyone who wants a precise hour."""
    labels = {
        7: t("delivery_hour.early_morning", lang),
        9: t("delivery_hour.morning", lang),
        12: t("delivery_hour.noon", lang),
        15: t("delivery_hour.afternoon", lang),
        18: t("delivery_hour.evening", lang),
        21: t("delivery_hour.night", lang),
    }
    rows = [
        [InlineKeyboardButton(text=labels[7], callback_data=f"{callback_prefix}:7"),
         InlineKeyboardButton(text=labels[9], callback_data=f"{callback_prefix}:9")],
        [InlineKeyboardButton(text=labels[12], callback_data=f"{callback_prefix}:12"),
         InlineKeyboardButton(text=labels[15], callback_data=f"{callback_prefix}:15")],
        [InlineKeyboardButton(text=labels[18], callback_data=f"{callback_prefix}:18"),
         InlineKeyboardButton(text=labels[21], callback_data=f"{callback_prefix}:21")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def snooze_keyboard(khatm_id: str, lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("portions.snooze_label.30", lang), callback_data=f"snooze:{khatm_id}:30"),
                InlineKeyboardButton(text=t("portions.snooze_label.60", lang), callback_data=f"snooze:{khatm_id}:60"),
                InlineKeyboardButton(text=t("portions.snooze_label.180", lang), callback_data=f"snooze:{khatm_id}:180"),
            ],
            [InlineKeyboardButton(text=t("portions.snooze_label.custom", lang), callback_data=f"snooze_custom:{khatm_id}")],
        ]
    )


def commitment_quantity_keyboard(khatm_id: str, lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text=t("portions.button.log_commitment_part", lang), callback_data=f"commitment_contribute:{khatm_id}"
        )]]
    )


# ---- R11 (owner 2026-09-28): member picks their own commitment mode ----------

def member_commitment_mode_keyboard(pid: str, lang: str = "fa") -> InlineKeyboardMarkup:
    """Two ways a member commits to a commitment khatm: a recurring schedule
    (REGULAR) or a one-off count they log themselves (COUNT)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("commit.mode.regular", lang), callback_data=f"cmode:regular:{pid}")],
            [InlineKeyboardButton(text=t("commit.mode.count", lang), callback_data=f"cmode:count:{pid}")],
        ]
    )


def commitment_freq_keyboard(pid: str, lang: str = "fa") -> InlineKeyboardMarkup:
    """REGULAR mode: how often to read."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("commit.freq.daily", lang), callback_data=f"cfreq:DAILY:{pid}")],
            [InlineKeyboardButton(text=t("commit.freq.weekly", lang), callback_data=f"cfreq:WEEKLY:{pid}")],
            [InlineKeyboardButton(text=t("commit.freq.monthly", lang), callback_data=f"cfreq:MONTHLY:{pid}")],
        ]
    )


def commitment_weekday_keyboard(pid: str, lang: str = "fa") -> InlineKeyboardMarkup:
    """WEEKLY anchor picker: 0=Saturday .. 6=Friday (Persian week order)."""
    days = [
        t("weekday.sat", lang), t("weekday.sun", lang), t("weekday.mon", lang),
        t("weekday.tue", lang), t("weekday.wed", lang), t("weekday.thu", lang),
        t("weekday.fri", lang),
    ]
    rows, row = [], []
    for i, label in enumerate(days):
        row.append(InlineKeyboardButton(text=label, callback_data=f"cdow:{i}:{pid}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def commitment_count_log_keyboard(pid: str, lang: str = "fa") -> InlineKeyboardMarkup:
    """COUNT mode: tap to log a batch you've read, or re-pledge a fresh count (R12)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("commit.count.log_one", lang), callback_data=f"clog:1:{pid}")],
            [InlineKeyboardButton(text=t("commit.count.log_custom", lang), callback_data=f"clogc:{pid}")],
            [InlineKeyboardButton(text=t("commit.count.new_pledge", lang), callback_data=f"cnew:{pid}")],
        ]
    )


def commitment_consent_keyboard(token: str, lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("join.button.accept_commitment", lang), callback_data=f"commitment_consent:accept:{token}")],
            [InlineKeyboardButton(text=t("join.button.cancel", lang), callback_data=f"commitment_consent:cancel:{token}")],
        ]
    )


def join_preview_keyboard(token: str, lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("join.button.join", lang), callback_data=f"join_preview:{token}")],
            [InlineKeyboardButton(text=t("join.button.cancel", lang), callback_data="join_preview:cancel")],
        ]
    )


def pause_duration_keyboard(khatm_id: str, lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("pause.duration.3", lang), callback_data=f"pause:{khatm_id}:3"),
                InlineKeyboardButton(text=t("pause.duration.7", lang), callback_data=f"pause:{khatm_id}:7"),
                InlineKeyboardButton(text=t("pause.duration.14", lang), callback_data=f"pause:{khatm_id}:14"),
            ],
            [InlineKeyboardButton(text=t("pause.duration.custom", lang), callback_data=f"pause_custom:{khatm_id}")],
        ]
    )


def leave_reason_keyboard(participation_id: str, lang: str = "fa") -> InlineKeyboardMarkup:
    reasons = [
        (t("leave.reason.busy", lang), "busy"),
        (t("leave.reason.mistake", lang), "mistake"),
        (t("leave.reason.notifications", lang), "notifications"),
        (t("leave.reason.other", lang), "other"),
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"leave_reason:{participation_id}:{code}")]
            for label, code in reasons
        ]
    )


def contribute_keyboard(khatm_id: str, lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text=t("portions.button.contribute", lang), callback_data=f"contribute:{khatm_id}"
        )]]
    )


def leave_all_keyboard(targets: list[tuple[str, str]]) -> InlineKeyboardMarkup | None:
    """One row per joined khatm: `targets` is a list of (title, participation_id).
    Attached to the "🕋 ختم‌های من" summary message itself — avoids sending a
    separate noisy message per khatm just for a leave button."""
    if not targets:
        return None
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"🚪 خروج از «{title}»", callback_data=f"leave_ask:{participation_id}")]
            for title, participation_id in targets
        ]
    )


def creator_khatm_keyboard(
    khatm_id: str, *, can_cancel: bool = True, lang: str = "fa"
) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text=t("cs.members", lang), callback_data=f"creator_report:members:{khatm_id}"),
            InlineKeyboardButton(text=t("cs.export", lang), callback_data=f"creator_report:export:{khatm_id}"),
        ],
        [
            InlineKeyboardButton(text=t("cs.qr", lang), callback_data=f"creator_report:qr:{khatm_id}"),
            InlineKeyboardButton(text=t("cs.stats", lang), callback_data=f"creator_report:stats:{khatm_id}"),
        ],
        [InlineKeyboardButton(text=t("cs.settings", lang), callback_data=f"cs:menu:{khatm_id}")],
    ]
    if can_cancel:
        rows[-1].append(InlineKeyboardButton(text=t("cs.cancel_khatm", lang), callback_data=f"cancel_khatm_ask:{khatm_id}"))
    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )


def creator_settings_keyboard(
    khatm_id: str,
    *,
    is_quran: bool,
    is_commitment: bool,
    is_open: bool,
    allow_skip_today: bool,
    allow_pause: bool,
    allow_snooze: bool,
    miss_threshold: int,
    miss_window_days: int,
    content_mode: str,
    lang: str = "fa",
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text=t("cs.title", lang), callback_data=f"cs:edit:{khatm_id}:title"),
            InlineKeyboardButton(text=t("cs.welcome", lang), callback_data=f"cs:edit:{khatm_id}:welcome"),
        ]
    ]
    rows.append([
        InlineKeyboardButton(text=t("cs.end_date", lang), callback_data=f"cs:end:{khatm_id}"),
        InlineKeyboardButton(text=t("cs.end_clear", lang), callback_data=f"cs:end_clear:{khatm_id}"),
    ])
    if is_open:
        rows.append([InlineKeyboardButton(text=t("cs.schedule", lang), callback_data=f"cs:schedule:{khatm_id}")])
    if is_quran:
        mode_labels = {
            "AUTO": t("cs.content_mode.auto", lang),
            "PHOTO": t("cs.content_mode.photo", lang),
            "TEXT": t("cs.content_mode.text", lang),
        }
        rows.append([InlineKeyboardButton(
            text=t("cs.content_fmt", lang, mode=mode_labels.get(content_mode, mode_labels["AUTO"])),
            callback_data=f"cs:modes:{khatm_id}",
        )])
    if is_commitment:
        rows.extend([
            [InlineKeyboardButton(
                text=f"{'✅' if allow_pause else '🚫'} {t('cs.pause_toggle', lang)}",
                callback_data=f"cs:pause:{khatm_id}",
            )],
            [InlineKeyboardButton(
                text=f"{'✅' if allow_snooze else '🚫'} {t('cs.snooze_toggle', lang)}",
                callback_data=f"cs:snooze:{khatm_id}",
            )],
        ])
    rows.append([InlineKeyboardButton(text=t("cs.back_my_khatms", lang), callback_data="my_khatms:open")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def creator_edit_cancel_keyboard(khatm_id: str, lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("cs.edit_cancel", lang), callback_data=f"cs:edit_cancel:{khatm_id}")]
    ])


def creator_content_mode_keyboard(khatm_id: str, lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("cs.mode_auto", lang), callback_data=f"cs:mode:{khatm_id}:AUTO")],
        [InlineKeyboardButton(text=t("cs.mode_photo", lang), callback_data=f"cs:mode:{khatm_id}:PHOTO")],
        [InlineKeyboardButton(text=t("cs.mode_text", lang), callback_data=f"cs:mode:{khatm_id}:TEXT")],
        [InlineKeyboardButton(text=t("cs.back", lang), callback_data=f"cs:menu:{khatm_id}")],
    ])


def creator_miss_policy_keyboard(khatm_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="حساس: ۱ دیرکرد در ۷ روز", callback_data=f"cs:miss:{khatm_id}:1:7")],
        [InlineKeyboardButton(text="متعادل: ۲ دیرکرد در ۷ روز", callback_data=f"cs:miss:{khatm_id}:2:7")],
        [InlineKeyboardButton(text="آسان‌گیر: ۳ دیرکرد در ۱۴ روز", callback_data=f"cs:miss:{khatm_id}:3:14")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data=f"cs:menu:{khatm_id}")],
    ])


def creator_schedule_keyboard(khatm_id: str, lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("cs.sched.off", lang), callback_data=f"cs:schedule_set:{khatm_id}:off")],
        [InlineKeyboardButton(text=t("cs.sched.daily", lang), callback_data=f"cs:schedule_set:{khatm_id}:daily")],
        [InlineKeyboardButton(text=t("cs.sched.workdays", lang), callback_data=f"cs:schedule_set:{khatm_id}:weekly:0,1,2,3,4")],
        [InlineKeyboardButton(text=t("cs.sched.weekend", lang), callback_data=f"cs:schedule_set:{khatm_id}:weekly:5,6")],
        [InlineKeyboardButton(text=t("cs.sched.every3", lang), callback_data=f"cs:schedule_set:{khatm_id}:every:3")],
        [InlineKeyboardButton(text=t("cs.sched.date", lang), callback_data=f"cs:schedule_date:{khatm_id}")],
        [InlineKeyboardButton(text=t("cs.back", lang), callback_data=f"cs:menu:{khatm_id}")],
    ])


def cancel_khatm_confirm_keyboard(khatm_id: str, lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("cs.cancel_confirm", lang), callback_data=f"cancel_khatm:{khatm_id}")],
            [InlineKeyboardButton(text=t("ck.cancel", lang), callback_data="cancel_khatm_cancel")],
        ]
    )




async def safe_clear_inline_keyboard(message: Message) -> None:
    """Best-effort: remove an inline keyboard after it's been acted on.
    Never raise — a double-tap or an already-edited message is not an error
    worth surfacing to the user."""
    try:
        await message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass


async def safe_answer_callback(callback: CallbackQuery, text: str | None = None, show_alert: bool = False) -> None:
    try:
        await callback.answer(text=text, show_alert=show_alert)
    except Exception:
        pass


import base64
import uuid

def pack_join_callback_data(prefix: str, khatm_id, user_id) -> str:
    """Pack two UUIDs into a short base64 string to fit in Telegram's 64-byte limit."""
    if isinstance(khatm_id, str): khatm_id = uuid.UUID(khatm_id)
    if isinstance(user_id, str): user_id = uuid.UUID(user_id)
    data = base64.urlsafe_b64encode(khatm_id.bytes + user_id.bytes).decode("ascii").rstrip("=")
    return f"{prefix}:{data}"

def unpack_join_callback_data(data: str) -> tuple[str, str]:
    """Unpack two UUIDs from a short base64 string."""
    b = base64.urlsafe_b64decode(data + "==")
    khatm_id = str(uuid.UUID(bytes=b[:16]))
    user_id = str(uuid.UUID(bytes=b[16:]))
    return khatm_id, user_id


async def bail_if_menu_button(message: Message, state: FSMContext) -> bool:
    """Call this first in every free-text wizard step. Returns True (and
    already replied + cleared state) if the user pressed a menu button
    instead of answering — the caller should `return` immediately in that
    case rather than treating the button label as their answer."""
    text = (message.text or "").strip()
    if text not in RESERVED_MENU_TEXTS and not text.startswith("/"):
        return False
    await state.clear()
    # Import lazily because navigation.py imports the keyboard builders.
    from khatmsaz.bot.navigation import resolve_home_navigation

    lang, role, keyboard = await resolve_home_navigation(message)
    key = "navigation.admin_interrupted" if role.value == "SUPER_ADMIN" else "navigation.interrupted"
    await message.answer(
        t(key, lang),
        reply_markup=keyboard,
    )
    return True
