"""`/start` handler — shared by both Telegram and Bale.

Resolves-or-provisions the canonical User for whichever chat just messaged
us. Two cases:
  - plain `/start` → welcome message + main menu.
  - `/start join_<token>` (a deep link from an invite) → register first if
    needed (DOMAIN_MODEL.md §1 — name/phone/province/city/gender, only once,
    only when someone actually tries to join something), then join (or, for
    a PRIVATE khatm, request to join — see `join_requests.py`).
No platform-specific logic here: the platform is read off
`message.bot.khatmsaz_platform`, set once when each Bot instance is
constructed (see bot/telegram/client.py, bot/bale/client.py).
"""

from html import escape

from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from khatmsaz.bot.keyboards import bail_if_menu_button, commitment_consent_keyboard, commitment_quantity_keyboard, contribute_keyboard, delivery_hour_keyboard, join_preview_keyboard, language_choice_keyboard, main_menu_keyboard, portion_done_keyboard, safe_clear_inline_keyboard
from khatmsaz.bot.notify_adapter import send_with_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.allocation.models import PortionUnitKind
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.invitation.service import InvitationExpiredError, InvitationNotFoundError
from khatmsaz.modules.khatm.models import CreatorDisplayMode, Khatm, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm_category import service as category_service
from khatmsaz.modules.khatm_workflow import service as workflow_service
from khatmsaz.modules.khatm_workflow.service import JoinRequiresApprovalError
from khatmsaz.modules.notification import service as notification_service
from khatmsaz.modules.participation.models import Participation
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.participation.service import AlreadyParticipatingError
from khatmsaz.modules.settings import service as settings_service

router = Router(name="start")

WELCOME_TEXT = t("welcome.text", "fa")


class AskDeliveryHour(StatesGroup):
    """Owner request (2026-09-21): every committed member should be asked
    what hour their daily portion should be auto-delivered, right at join
    time — not left to silently default to hour 9 unless they happen to
    discover the hidden `/reminder` command themselves (mirrors the
    open-Quran reading setup wizard in `portions.py`)."""

    entering_hour = State()


def _creator_display_name(khatm: Khatm, creator) -> str:
    mode = getattr(khatm, "creator_display_mode", CreatorDisplayMode.FULL_NAME.value)
    if mode == CreatorDisplayMode.ANONYMOUS.value:
        return "یک نیکوکار"
    if mode == CreatorDisplayMode.PSEUDONYM.value:
        return getattr(khatm, "creator_pseudonym", None) or "یک نیکوکار"
    name = creator.display_name if creator is not None and creator.display_name else ""
    return name.split()[0] if mode == CreatorDisplayMode.FIRST_NAME and name else name


def build_join_preview_message(
    khatm: Khatm,
    creator_name: str,
    member_count: int,
    lang: str = "fa",
    *,
    category_title: str | None = None,
    category_group: str | None = None,
) -> str:
    """Owner complaint (2026-09-20): the old preview only showed title/
    creator/niyyat/member-count — it never explained *what kind* of khatm
    this is or *what committing to it actually means*, which is exactly
    the information someone needs before tapping join. `category_title`/
    `category_group` (for SALAWAT-family khatms) must be resolved by the
    caller from `content_category_id`, since this function stays sync."""
    text = t("join.preview.header", lang)
    text += t("join.preview.title", lang, title=escape(khatm.title))
    text += t(
        "join.preview.creator", lang,
        creator=escape(creator_name or t("join.creator_display.anonymous", lang)),
    )
    if khatm.niyyat:
        text += t("join.preview.niyyat", lang, niyyat=escape(khatm.niyyat))

    if khatm.template_type == KhatmTemplateType.QURAN_PAGE:
        text += t("join.preview.type_line", lang, icon="📖", type=t("join.preview.type_quran", lang))
        if khatm.khatm_type == KhatmTypeEnum.COMMITMENT:
            text += t("join.preview.mode_commitment_quran", lang)
        else:
            text += t("join.preview.mode_open_quran", lang)
    else:
        type_key = {
            "DUA": "join.preview.type_dua",
            "LAAN": "join.preview.type_laan",
        }.get(category_group or "SALAWAT", "join.preview.type_salawat")
        type_label = t(type_key, lang)
        if category_title:
            text += t("join.preview.type_line_with_category", lang, icon="📿", type=type_label, category=escape(category_title))
        else:
            text += t("join.preview.type_line", lang, icon="📿", type=type_label)
        if khatm.khatm_type == KhatmTypeEnum.COMMITMENT and khatm.repetition_target:
            unit = t("create_khatm.unit.salawat", lang) if (category_group or "SALAWAT") == "SALAWAT" else t("create_khatm.unit.time", lang)
            text += t("join.preview.mode_commitment_quantified", lang, count=khatm.repetition_target, unit=unit)
        else:
            text += t("join.preview.mode_open_generic", lang)

    text += t("join.preview.member_count", lang, count=member_count)
    if khatm.welcome_text:
        text += t("join.preview.welcome_text", lang, text=escape(khatm.welcome_text))
    return text + t("join.preview.cta", lang)


@router.message(CommandStart(deep_link=True))
async def handle_start_with_payload(message: Message, command: CommandObject, state: FSMContext) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    payload = command.args or ""

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)

        if payload.startswith("join_"):
            token = payload.removeprefix("join_")
            viewer_settings = await settings_service.get_or_create(session, user.id)
            lang = viewer_settings.language
            try:
                khatm_id = await invitation_service.resolve_khatm_id(session, token)
            except InvitationNotFoundError:
                await message.answer(t("join.error.invalid_link", lang), reply_markup=main_menu_keyboard(lang))
                return
            except InvitationExpiredError:
                await message.answer(t("join.error.expired_link", lang), reply_markup=main_menu_keyboard(lang))
                return
            khatm = await khatm_service.get_khatm(session, khatm_id)
            if khatm is None:
                await message.answer(t("join.error.khatm_gone", lang), reply_markup=main_menu_keyboard(lang))
                return
            creator = await identity_service.find_by_id(session, khatm.creator_user_id)
            member_count = await participation_service.count_for_khatm(session, khatm.id)
            category_title = None
            category_group = None
            if khatm.template_type == KhatmTemplateType.SALAWAT:
                if khatm.content_category_id:
                    category = await category_service.get(session, khatm.content_category_id)
                    if category is not None:
                        category_title = category.title
                        category_group = category.group.value
                else:
                    category_group = "SALAWAT"
            await state.update_data(pending_join_token=token)
            if khatm.cover_status == "APPROVED" and khatm.cover_platform == platform.value and khatm.cover_ref:
                await message.answer_photo(khatm.cover_ref, caption=t("join.cover_caption", lang))
            await message.answer(
                build_join_preview_message(
                    khatm, _creator_display_name(khatm, creator), member_count, lang,
                    category_title=category_title, category_group=category_group,
                ),
                reply_markup=join_preview_keyboard(token),
            )
            return

    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.callback_query(F.data.startswith("join_preview:"))
async def accept_join_preview(callback, state: FSMContext) -> None:
    token = callback.data.split(":", 1)[1]
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    if token == "cancel":
        await state.clear()
        await safe_clear_inline_keyboard(callback.message)
        async with session_scope() as _sess:
            _user = await identity_service.resolve_or_provision_user(_sess, platform, callback.from_user.id)
            _settings = await settings_service.get_or_create(_sess, _user.id)
            _lang = _settings.language
        await callback.message.answer(t("join.cancelled", _lang), reply_markup=main_menu_keyboard(_lang))
        return
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        await safe_clear_inline_keyboard(callback.message)
        if not await settings_service.is_registered(session, user.id) or not user.display_name:
            from khatmsaz.bot.handlers.registration import start_registration
            await start_registration(callback.message, state, pending_join_token=token)
        else:
            await resume_join_after_registration(callback.message, session, user.id, token, state=state)
    await callback.answer()


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        already_prompted = settings.language_prompted
        lang = settings.language

    if already_prompted:
        is_creator = user.role in (UserRole.CREATOR, UserRole.SUPER_ADMIN)
        await message.answer(t("welcome.text", lang), reply_markup=main_menu_keyboard(lang, is_creator))
        return

    # First-ever /start (owner request, 2026-09-20): show the welcome
    # message, then ask the language right after it — every button/menu
    # from here on uses whatever they pick. Marked prompted immediately so
    # a user who ignores the prompt isn't asked again on every later /start.
    await message.answer(WELCOME_TEXT)
    async with session_scope() as session:
        await settings_service.mark_language_prompted(session, user.id)
    await message.answer(t("language.prompt", lang), reply_markup=language_choice_keyboard())


@router.callback_query(F.data.startswith("first_lang:"))
async def choose_first_language(callback, state: FSMContext) -> None:
    lang = callback.data.split(":", 1)[1]
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.fromuser.id if hasattr(callback, 'fromuser') else callback.from_user.id)
        is_creator = user.role in (UserRole.CREATOR, UserRole.SUPER_ADMIN)
        try:
            await settings_service.set_language(session, user.id, lang)
        except ValueError:
            await callback.answer()
            return
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    
    # Send the onboarding info text
    await callback.message.answer(t("creator_request.info_text", lang))
    await callback.message.answer(t("language.saved", lang), reply_markup=main_menu_keyboard(lang, is_creator))
    await callback.answer()


def build_join_success_message(
    khatm: Khatm,
    participation: Participation,
    first_portion,
    was_waitlisted: bool,
    display_name: str,
    creator_display_name: str = "",
    lang: str = "fa",
):
    """Shared with `join_requests.py`'s approval handler, which sends this
    same message to a requester who may be on a different platform than
    whoever approved them — via `notify_adapter`, not `message.answer`.
    `lang` must be the *recipient's* (the joining user's) own stored
    language, not the approver's."""
    text = t("join.welcome_line", lang, name=escape(display_name), title=escape(khatm.title))
    if creator_display_name:
        text += t("join.creator_line", lang, name=escape(creator_display_name))
    if khatm.niyyat:
        text += t("join.niyyat_line", lang, niyyat=escape(khatm.niyyat))
    if khatm.welcome_text:
        text += t("join.welcome_text_line", lang, text=escape(khatm.welcome_text))

    if was_waitlisted:
        text += t("join.waitlisted_line", lang)
        return text, contribute_keyboard(str(khatm.id), lang)

    if first_portion is not None and first_portion.unit_kind == PortionUnitKind.POSITIONAL:
        text += t("join.first_page_portion_line", lang, start=first_portion.unit_start, end=first_portion.unit_end)
        return text, portion_done_keyboard(str(khatm.id), allow_skip_today=khatm.allow_skip_today, allow_snooze=bool(khatm.allow_snooze), lang=lang)

    if first_portion is not None and first_portion.unit_kind == PortionUnitKind.QUANTITY:
        text += t("join.first_quantity_portion_line", lang, quantity=first_portion.quantity)
        return text, commitment_quantity_keyboard(str(khatm.id), lang)

    if khatm.khatm_type == KhatmTypeEnum.COMMITMENT and khatm.template_type == KhatmTemplateType.QURAN_PAGE:
        text += t("join.no_open_portion_line", lang)
        return text, main_menu_keyboard(lang)

    return text, contribute_keyboard(str(khatm.id), lang)


async def resume_join_after_registration(
    message: Message, session, user_id, token: str, *, state: FSMContext | None = None, consent_accepted: bool = False
) -> None:
    """The actual join logic — public because `registration.py` calls this
    once a first-time joiner finishes their profile."""
    _user_settings = await settings_service.get_or_create(session, user_id)
    _lang = _user_settings.language
    if not consent_accepted:
        khatm_id = await invitation_service.resolve_khatm_id(session, token)
        khatm_preview = await khatm_service.get_khatm(session, khatm_id)
        if khatm_preview is not None and khatm_preview.khatm_type == KhatmTypeEnum.COMMITMENT:
            if state is not None:
                await state.update_data(pending_commitment_token=token)
            await message.answer(
                t("join.commitment_consent", _lang),
                reply_markup=commitment_consent_keyboard(token),
            )
            return
    try:
        khatm, participation, first_portion, was_waitlisted = await workflow_service.join_via_token(
            session, token=token, user_id=user_id
        )
    except InvitationNotFoundError:
        await message.answer(t("join.error.invalid_link", _lang), reply_markup=main_menu_keyboard(_lang))
        return
    except InvitationExpiredError:
        await message.answer(t("join.error.expired_link", _lang), reply_markup=main_menu_keyboard(_lang))
        return
    except AlreadyParticipatingError:
        await message.answer(t("join.error.already_member", _lang), reply_markup=main_menu_keyboard(_lang))
        return
    except JoinRequiresApprovalError as exc:
        await _request_private_join(message, session, exc.khatm, user_id, _lang)
        return
    except workflow_service.KhatmUnavailableError:
        await message.answer(t("join.error.khatm_ended", _lang), reply_markup=main_menu_keyboard(_lang))
        return

    if khatm is None:
        await message.answer(t("join.error.khatm_gone", _lang), reply_markup=main_menu_keyboard(_lang))
        return

    await invitation_service.mark_accepted(session, token, user_id)

    user = await identity_service.find_by_platform(
        session, getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM), str(message.chat.id)
    )
    lang = _lang  # already resolved above before join attempt
    display_name = user.display_name if user is not None and user.display_name else (
        message.from_user.full_name if message.from_user else ""
    )
    creator = await identity_service.find_by_id(session, khatm.creator_user_id)
    creator_display_name = ""
    creator_mode = getattr(khatm, "creator_display_mode", CreatorDisplayMode.FULL_NAME.value)
    if creator_mode == CreatorDisplayMode.ANONYMOUS.value:
        creator_display_name = t("join.creator_display.anonymous", lang)
    elif creator_mode == CreatorDisplayMode.PSEUDONYM.value:
        creator_display_name = getattr(khatm, "creator_pseudonym", None) or t("join.creator_display.anonymous", lang)
    elif creator is not None and creator.display_name:
        creator_display_name = creator.display_name
        if creator_mode == CreatorDisplayMode.FIRST_NAME:
            creator_display_name = creator_display_name.split()[0]
    text, keyboard = build_join_success_message(
        khatm, participation, first_portion, was_waitlisted, display_name, creator_display_name, lang
    )
    await message.answer(text, reply_markup=keyboard)

    # Owner request (2026-09-21/22): ask every freshly-joined member what
    # hour they'd like their daily nudge/portion sent, instead of silently
    # defaulting to hour 9 unless they discover the hidden `/reminder`
    # command themselves. Originally only fired for a fresh COMMITMENT
    # portion; owner reported creating an OPEN dua khatm and not being
    # asked at all — `_send_open_schedule_reminders` also uses each
    # participant's own reminder hour, it just never asked either. Now
    # fires for both: a fresh commitment portion, OR a fresh OPEN-khatm
    # join. Only once — skipped if this participation already has a
    # preference (e.g. re-joined via some other path, or already set one).
    is_fresh_commitment = not was_waitlisted and first_portion is not None
    is_fresh_open_join = not was_waitlisted and first_portion is None and khatm.khatm_type == KhatmTypeEnum.OPEN
    if (
        state is not None and (is_fresh_commitment or is_fresh_open_join)
        and await notification_service.get_preference(session, participation.id) is None
    ):
        await state.set_state(AskDeliveryHour.entering_hour)
        await state.update_data(delivery_hour_participation_id=str(participation.id), lang=lang)
        await message.answer(t("join.ask_delivery_hour", lang), reply_markup=delivery_hour_keyboard("join_hour", lang))


async def _save_delivery_time(participation_id: str, hour: int, minute: int = 0) -> None:
    async with session_scope() as session:
        await notification_service.set_reminder_preference(
            session, participation_id, reminder_hour=hour, reminder_minute=minute, enabled=True
        )


def _parse_delivery_time(raw: str) -> tuple[int, int] | None:
    """Parse 'H', 'HH', or 'HH:MM' into (hour, minute). Returns None if invalid."""
    raw = raw.strip()
    if ":" in raw:
        parts = raw.split(":", 1)
        if not parts[0].isdigit() or not parts[1].isdigit():
            return None
        h, m = int(parts[0]), int(parts[1])
        if 0 <= h <= 23 and 0 <= m <= 59:
            return h, m
        return None
    if raw.isdigit():
        h = int(raw)
        if 0 <= h <= 23:
            return h, 0
    return None


@router.callback_query(F.data.startswith("join_hour:"), AskDeliveryHour.entering_hour)
async def receive_delivery_hour_button(callback, state: FSMContext) -> None:
    hour = int(callback.data.split(":", 1)[1])
    data = await state.get_data()
    lang = data.get("lang", "fa")
    participation_id = data.get("delivery_hour_participation_id")
    await state.clear()
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    if participation_id:
        await _save_delivery_time(participation_id, hour, 0)
    await callback.message.answer(t("join.delivery_hour_saved", lang, hour=hour), reply_markup=main_menu_keyboard(lang))
    await callback.answer()


@router.message(AskDeliveryHour.entering_hour)
async def receive_delivery_hour(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
    data = await state.get_data()
    lang = data.get("lang", "fa")
    raw = (message.text or "").strip()
    parsed = _parse_delivery_time(raw)
    if parsed is None:
        await message.answer(t("join.delivery_hour_invalid", lang))
        return
    hour, minute = parsed
    participation_id = data.get("delivery_hour_participation_id")
    await state.clear()
    if participation_id:
        await _save_delivery_time(participation_id, hour, minute)
    time_str = f"{hour:02d}:{minute:02d}"
    await message.answer(t("join.delivery_hour_saved", lang, hour=time_str), reply_markup=main_menu_keyboard(lang))


@router.callback_query(F.data.startswith("commitment_consent:accept"))
async def accept_commitment(callback, state: FSMContext) -> None:
    data = await state.get_data()
    callback_parts = callback.data.split(":", 2)
    token = callback_parts[2] if len(callback_parts) == 3 else data.get("pending_commitment_token")
    if not token:
        # Lang not available here without a DB call; use fa as safe default for a transient error message.
        await callback.answer(t("join.commitment_expired", "fa"), show_alert=True)
        return
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        await state.update_data(pending_commitment_token=None)
        await callback.answer()
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await state.clear()
        await resume_join_after_registration(
            callback.message, session, user.id, token, state=state, consent_accepted=True
        )


@router.callback_query(F.data.startswith("commitment_consent:cancel"))
async def cancel_commitment(callback, state: FSMContext) -> None:
    await state.clear()
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as _sess:
        _u = await identity_service.resolve_or_provision_user(_sess, platform, callback.from_user.id)
        _s = await settings_service.get_or_create(_sess, _u.id)
        _lang = _s.language
    await callback.answer(t("join.commitment_expired", _lang), show_alert=False)
    await callback.message.answer(t("join.commitment_cancelled", _lang), reply_markup=main_menu_keyboard(_lang))


async def _request_private_join(message: Message, session, khatm: Khatm, user_id, lang: str = "fa") -> None:
    requester = await identity_service.find_by_id(session, user_id)
    requester_name = requester.display_name if requester and requester.display_name else t("join.default_display_name", lang)
    creator_identities = await identity_service.list_identities_for_user(session, khatm.creator_user_id)

    await message.answer(
        t("join.private_request_sent", lang, title=khatm.title),
        reply_markup=main_menu_keyboard(lang),
    )

    text = f"{requester_name} می‌خواد به ختم خصوصی «{khatm.title}» بپیونده."
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ تایید عضویت", callback_data=f"approve_join:{khatm.id}:{user_id}"),
                InlineKeyboardButton(text="❌ رد", callback_data=f"reject_join:{khatm.id}:{user_id}"),
            ]
        ]
    )
    for identity in creator_identities:
        await send_with_keyboard(identity.platform.value, identity.subject, text, keyboard)
