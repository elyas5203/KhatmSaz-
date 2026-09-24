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
)

def participant_menu_keyboard(lang: str = "fa") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("menu.today", lang))],
            [KeyboardButton(text=t("menu.public_khatms", lang))],
            [KeyboardButton(text=t("menu.settings", lang)), KeyboardButton(text=t("menu.help", lang))],
            [KeyboardButton(text=t("menu.support", lang))],
        ],
        resize_keyboard=True,
    )

def support_inline_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("support.button.send_message", lang), callback_data="suggest:start")],
            [InlineKeyboardButton(text=t("menu.creator_request", lang), callback_data="creator_request:start")],
        ]
    )

def back_to_support_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("button.back", lang), callback_data="support:menu")]
        ]
    )



def creator_menu_keyboard(lang: str = "fa") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("menu.today", lang)), KeyboardButton(text=t("menu.my_khatms", lang))],
            [KeyboardButton(text=t("menu.report", lang)), KeyboardButton(text=t("menu.settings", lang))],
            [KeyboardButton(text=t("menu.create", lang)), KeyboardButton(text=t("menu.help", lang))],
        ],
        resize_keyboard=True,
    )

def main_menu_keyboard(lang: str = "fa", is_creator: bool = False) -> ReplyKeyboardMarkup:
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


def help_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("help.button.join", lang), callback_data="help:join"),
                InlineKeyboardButton(text=t("help.button.portion", lang), callback_data="help:portion"),
            ],
            [
                InlineKeyboardButton(text=t("help.button.create", lang), callback_data="help:create"),
                InlineKeyboardButton(text=t("help.button.wallet", lang), callback_data="help:wallet"),
            ],
            [
                InlineKeyboardButton(text=t("help.button.settings", lang), callback_data="help:settings"),
                InlineKeyboardButton(text=t("help.button.manage", lang), callback_data="help:manage"),
            ],
            [InlineKeyboardButton(text=t("suggestions.button.open", lang), callback_data="suggest:start")],
        ]
    )


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


def help_manage_actions_keyboard(lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("help.button.my_khatms", lang), callback_data="my_khatms:open")],
            [InlineKeyboardButton(text=t("help.button.creator_panel", lang), callback_data="creator:web_login")],
            [InlineKeyboardButton(text=t("help.button.admin_panel", lang), callback_data="admin:web_login")],
            [InlineKeyboardButton(text=t("help.button.back", lang), callback_data="help:home")],
        ]
    )


def commitment_mode_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔒 تعهدی (سهم مشخص برای هرکس)", callback_data="ck:mode:COMMITMENT")],
            [InlineKeyboardButton(text="🌿 آزاد (هرکس با میل خودش)", callback_data="ck:mode:OPEN")],
        ]
    )


def template_choice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 ختم صفحات قرآن", callback_data="ck:tpl:QURAN_PAGE")],
            [InlineKeyboardButton(text="📿 ختم صلوات", callback_data="ck:group:SALAWAT")],
            [InlineKeyboardButton(text="🤲 ختم دعا و زیارت", callback_data="ck:group:DUA")],
            [InlineKeyboardButton(text="🗡 ختم لعن", callback_data="ck:group:LAAN")],
        ]
    )


_CATEGORY_GROUP_EMOJI = {"SALAWAT": "📿", "LAAN": "🗡", "DUA": "🤲"}


def category_choice_keyboard(
    categories: list, *, group: str, allow_custom_request: bool = False
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
        rows.append([InlineKeyboardButton(text="➕ دعا یا زیارت دیگر", callback_data="ck:cat:custom")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def skip_niyyat_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="رد کردن ⏭", callback_data="ck:skip_niyyat")]]
    )


def edition_choice_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=info["label"], callback_data=f"ck:edition:{key}")]
        for key in QURAN_CREATION_EDITION_IDS
        for info in [QURAN_EDITIONS[key]]
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def content_delivery_mode_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ خودکار (هرچه موجود بود)", callback_data="ck:content_mode:AUTO")],
            [InlineKeyboardButton(text="🖼 فقط تصویر صفحات", callback_data="ck:content_mode:PHOTO")],
            [InlineKeyboardButton(text="📝 فقط متن صفحات", callback_data="ck:content_mode:TEXT")],
        ]
    )


def reminder_tone_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌱 صمیمی", callback_data="ck:tone:FRIENDLY")],
            [InlineKeyboardButton(text="📜 رسمی", callback_data="ck:tone:FORMAL")],
            [InlineKeyboardButton(text="🤍 معنوی", callback_data="ck:tone:DEVOTIONAL")],
            [InlineKeyboardButton(text="⚡ کوتاه", callback_data="ck:tone:SHORT")],
        ]
    )


def creator_display_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 نام کامل", callback_data="ck:creator_display:FULL_NAME")],
            [InlineKeyboardButton(text="🙂 فقط نام کوچک", callback_data="ck:creator_display:FIRST_NAME")],
            [InlineKeyboardButton(text="🪪 نام مستعار", callback_data="ck:creator_display:PSEUDONYM")],
            [InlineKeyboardButton(text="🤲 ناشناس / نیکوکار", callback_data="ck:creator_display:ANONYMOUS")],
        ]
    )


def start_schedule_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ همین حالا", callback_data="ck:start:now")],
            [InlineKeyboardButton(text="🗓 شروع در تاریخ آینده", callback_data="ck:start:future")],
        ]
    )


def capacity_choice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔢 ظرفیت محدود", callback_data="ck:capacity:limited")],
            [InlineKeyboardButton(text="♾ نامحدود", callback_data="ck:capacity:unlimited")],
        ]
    )


def visibility_choice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌍 عمومی (در فهرست ختم‌ها نمایش داده شود)", callback_data="ck:visibility:PUBLIC")],
            [InlineKeyboardButton(text="🔗 با لینک، برای همه باز", callback_data="ck:visibility:UNLISTED")],
            [InlineKeyboardButton(text="🔒 عضویت نیاز به تایید من داره", callback_data="ck:visibility:PRIVATE")],
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


def advertising_choice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ بله، تبلیغات فعال باشد", callback_data="ck:ads:ON")],
            [InlineKeyboardButton(text="🚫 خیر، بدون تبلیغات", callback_data="ck:ads:OFF")],
        ]
    )


def confirm_keyboard(*, allow_coupon: bool = False) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text="✅ تایید و شروع ختم", callback_data="ck:confirm")]]
    if allow_coupon:
        rows.append([InlineKeyboardButton(text="🎟 کد تخفیف دارم", callback_data="ck:coupon")])
    rows.append([InlineKeyboardButton(text="❌ انصراف", callback_data="ck:cancel")])
    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )


def coupon_entry_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 ادامه بدون کد", callback_data="ck:coupon_back")],
            [InlineKeyboardButton(text="❌ انصراف", callback_data="ck:cancel")],
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


def snooze_keyboard(khatm_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="۳۰ دقیقه", callback_data=f"snooze:{khatm_id}:30"),
                InlineKeyboardButton(text="۱ ساعت", callback_data=f"snooze:{khatm_id}:60"),
                InlineKeyboardButton(text="۳ ساعت", callback_data=f"snooze:{khatm_id}:180"),
            ],
            [InlineKeyboardButton(text="🗓 زمان دلخواه", callback_data=f"snooze_custom:{khatm_id}")],
        ]
    )


def commitment_quantity_keyboard(khatm_id: str, lang: str = "fa") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text=t("portions.button.log_commitment_part", lang), callback_data=f"commitment_contribute:{khatm_id}"
        )]]
    )


def commitment_consent_keyboard(token: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ تعهد را می‌پذیرم", callback_data=f"commitment_consent:accept:{token}")],
            [InlineKeyboardButton(text="❌ انصراف", callback_data=f"commitment_consent:cancel:{token}")],
        ]
    )


def join_preview_keyboard(token: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ شرکت در این ختم", callback_data=f"join_preview:{token}")],
            [InlineKeyboardButton(text="❌ انصراف", callback_data="join_preview:cancel")],
        ]
    )


def pause_duration_keyboard(khatm_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="۳ روز", callback_data=f"pause:{khatm_id}:3"),
                InlineKeyboardButton(text="۷ روز", callback_data=f"pause:{khatm_id}:7"),
                InlineKeyboardButton(text="۱۴ روز", callback_data=f"pause:{khatm_id}:14"),
            ],
            [InlineKeyboardButton(text="🗓 تا تاریخ مشخص", callback_data=f"pause_custom:{khatm_id}")],
        ]
    )


def leave_reason_keyboard(participation_id: str) -> InlineKeyboardMarkup:
    reasons = [
        ("فعلاً وقت ندارم", "busy"),
        ("اشتباهی عضو شدم", "mistake"),
        ("مشکل در دریافت پیام", "notifications"),
        ("سایر", "other"),
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
    khatm_id: str, *, can_cancel: bool = True, completion_announcement_enabled: bool = True
) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="👥 اعضا", callback_data=f"creator_report:members:{khatm_id}"),
            InlineKeyboardButton(text="⚠️ توجه", callback_data=f"creator_report:attention:{khatm_id}"),
        ],
        [InlineKeyboardButton(text="📄 خروجی CSV", callback_data=f"creator_report:export:{khatm_id}")],
        [
            InlineKeyboardButton(text="📈 آمار ختم", callback_data=f"creator_report:stats:{khatm_id}"),
            InlineKeyboardButton(text="🔳 QR دعوت", callback_data=f"creator_report:qr:{khatm_id}"),
        ],
        [InlineKeyboardButton(
            text=("🔔 پیام پایان: روشن" if completion_announcement_enabled else "🔕 پیام پایان: خاموش"),
            callback_data=f"cat:{khatm_id}",
        )],
        [InlineKeyboardButton(text="⚙️ تنظیمات ختم", callback_data=f"cs:menu:{khatm_id}")],
    ]
    if can_cancel:
        rows.append([InlineKeyboardButton(text="🗑 لغو ختم", callback_data=f"cancel_khatm_ask:{khatm_id}")])
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
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text="✏️ عنوان", callback_data=f"cs:edit:{khatm_id}:title"),
            InlineKeyboardButton(text="💬 پیام خوش‌آمد", callback_data=f"cs:edit:{khatm_id}:welcome"),
        ]
    ]
    rows.append([
        InlineKeyboardButton(text="🗓 پایان تاریخی", callback_data=f"cs:end:{khatm_id}"),
        InlineKeyboardButton(text="🧹 حذف پایان", callback_data=f"cs:end_clear:{khatm_id}"),
    ])
    if is_open:
        rows.append([InlineKeyboardButton(text="⏰ زمان‌بندی مشارکت", callback_data=f"cs:schedule:{khatm_id}")])
    if is_quran:
        mode_labels = {"AUTO": "خودکار", "PHOTO": "فقط تصویر", "TEXT": "فقط متن"}
        rows.append([InlineKeyboardButton(
            text=f"📖 فرمت محتوا: {mode_labels.get(content_mode, 'خودکار')}",
            callback_data=f"cs:modes:{khatm_id}",
        )])
    if is_commitment:
        rows.extend([
            [InlineKeyboardButton(
                text=f"{'✅' if allow_pause else '🚫'} توقف موقت تعهد",
                callback_data=f"cs:pause:{khatm_id}",
            )],
            [InlineKeyboardButton(
                text=f"{'✅' if allow_snooze else '🚫'} تعویق یادآوری",
                callback_data=f"cs:snooze:{khatm_id}",
            )],
        ])
    rows.append([InlineKeyboardButton(text="🔙 ختم‌های من", callback_data="my_khatms:open")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def creator_edit_cancel_keyboard(khatm_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 انصراف و بازگشت", callback_data=f"cs:edit_cancel:{khatm_id}")]
    ])


def creator_content_mode_keyboard(khatm_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ خودکار (پیشنهادی)", callback_data=f"cs:mode:{khatm_id}:AUTO")],
        [InlineKeyboardButton(text="🖼 فقط تصویر", callback_data=f"cs:mode:{khatm_id}:PHOTO")],
        [InlineKeyboardButton(text="📝 فقط متن", callback_data=f"cs:mode:{khatm_id}:TEXT")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data=f"cs:menu:{khatm_id}")],
    ])


def creator_miss_policy_keyboard(khatm_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="حساس: ۱ دیرکرد در ۷ روز", callback_data=f"cs:miss:{khatm_id}:1:7")],
        [InlineKeyboardButton(text="متعادل: ۲ دیرکرد در ۷ روز", callback_data=f"cs:miss:{khatm_id}:2:7")],
        [InlineKeyboardButton(text="آسان‌گیر: ۳ دیرکرد در ۱۴ روز", callback_data=f"cs:miss:{khatm_id}:3:14")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data=f"cs:menu:{khatm_id}")],
    ])


def creator_schedule_keyboard(khatm_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 بدون زمان‌بندی", callback_data=f"cs:schedule_set:{khatm_id}:off")],
        [InlineKeyboardButton(text="📅 هر روز", callback_data=f"cs:schedule_set:{khatm_id}:daily")],
        [InlineKeyboardButton(text="💼 روزهای کاری", callback_data=f"cs:schedule_set:{khatm_id}:weekly:0,1,2,3,4")],
        [InlineKeyboardButton(text="🌿 آخرهفته", callback_data=f"cs:schedule_set:{khatm_id}:weekly:5,6")],
        [InlineKeyboardButton(text="🔁 هر ۳ روز", callback_data=f"cs:schedule_set:{khatm_id}:every:3")],
        [InlineKeyboardButton(text="🗓 یک تاریخ مشخص", callback_data=f"cs:schedule_date:{khatm_id}")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data=f"cs:menu:{khatm_id}")],
    ])


def cancel_khatm_confirm_keyboard(khatm_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ لغو و بازپرداخت", callback_data=f"cancel_khatm:{khatm_id}")],
            [InlineKeyboardButton(text="❌ انصراف", callback_data="cancel_khatm_cancel")],
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


async def bail_if_menu_button(message: Message, state: FSMContext) -> bool:
    """Call this first in every free-text wizard step. Returns True (and
    already replied + cleared state) if the user pressed a menu button
    instead of answering — the caller should `return` immediately in that
    case rather than treating the button label as their answer."""
    if (message.text or "").strip() not in RESERVED_MENU_TEXTS:
        return False
    await state.clear()
    await message.answer(
        "این مرحله لغو شد. لطفاً دوباره روی همون دکمه بزنید.",
        reply_markup=main_menu_keyboard(),
    )
    return True
