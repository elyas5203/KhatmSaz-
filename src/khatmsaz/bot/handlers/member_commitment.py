"""R11/N2 (owner 2026-09-28, revised after live QA): member picks HOW they commit.

The creator sets only the khatm TOTAL. Each member then chooses, with the fewest
questions and an ephemeral chat (each step deletes the previous bot prompt AND
the member's own typed answer so nothing piles up):

  • COUNT   — pledge a number, log progress with a button, re-pledge when done.
  • REGULAR — freq (daily/weekly/monthly) → «چند بار در [روز/هفته/ماه]؟» → an exact
    reminder time (preset button or a typed HH:MM like «۱۳:۲۵»). The reminder
    engine notifies at that exact local time, once per period.

Entry point `start_commitment_mode_picker` is called from the join flow right
after a member joins a repetition-based COMMITMENT khatm.
"""
from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from khatmsaz.bot.keyboards import (
    commitment_count_log_keyboard,
    commitment_freq_keyboard,
    commitment_hour_keyboard,
    commitment_weekday_keyboard,
    member_commitment_back_keyboard,
    member_commitment_mode_keyboard,
    member_menu_keyboard,
    main_menu_keyboard,
    safe_answer_callback,
    safe_clear_inline_keyboard,
)
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.bot_registry.models import BotRole
from khatmsaz.bot.member_scope import participation_matches_bot
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.open_contribution import service as open_contribution_service
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.participation.commitment import CommitmentMode, ScheduleFreq, parse_hhmm
from khatmsaz.modules.participation.models import ParticipationStatus
from khatmsaz.modules.settings import service as settings_service

router = Router(name="member_commitment")


class CommitFlow(StatesGroup):
    entering_count = State()           # COUNT: pledge amount (also re-pledge)
    entering_log_amount = State()      # COUNT: custom log amount
    choosing_weekdays = State()        # REGULAR + WEEKLY: multi-select days (owner L4)
    entering_times_per_period = State()  # REGULAR: how many times per day/week
    entering_custom_time = State()     # REGULAR: typed exact HH:MM


def _lang_of(obj) -> str:
    bot = obj.bot
    if getattr(bot, "khatmsaz_role", BotRole.CREATOR) == BotRole.MEMBER:
        return getattr(bot, "khatmsaz_language", "fa")
    return "fa"


def _home_markup(obj):
    lang = _lang_of(obj)
    if getattr(obj.bot, "khatmsaz_role", BotRole.CREATOR) == BotRole.MEMBER:
        return member_menu_keyboard(lang)
    return main_menu_keyboard(lang)


async def _mwiz(message: Message, state: FSMContext, text: str, reply_markup=None):
    """Edit the one join-owned prompt and remove only typed setup replies."""
    data = await state.get_data()
    prev = data.get("_cwiz_mid")
    if getattr(getattr(message, "from_user", None), "is_bot", True) is False:
        try:
            await message.bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
    summary = (data.get("commit_summary") or "").strip()
    rendered = f"{summary}\n\n{text}" if summary and summary not in text else text
    sent = None
    if prev:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id, message_id=prev,
                text=rendered, reply_markup=reply_markup,
            )
            sent = type("EditedJoinMessage", (), {"message_id": prev})()
        except Exception:
            pass
    if sent is None:
        sent = await message.answer(rendered, reply_markup=reply_markup)
    await state.update_data(_cwiz_mid=getattr(sent, "message_id", None))
    return sent


def _question(text: str) -> str:
    return f"❓ <b>سؤال این مرحله</b>\n{text}"


def _retry_question(error: str, question: str) -> str:
    return f"⚠️ {error}\n\n{_question(question)}"


async def start_commitment_mode_picker(
    message: Message, state: FSMContext, participation_id, lang: str, *, summary: str = "",
    family=None,
) -> None:
    """Create one separate question message; the welcome card stays fixed above."""
    combined = "\n\n".join(part for part in (
        t("commit.explain", lang).strip(), _question(t("commit.ask_mode", lang).strip()),
    ) if part)
    markup = member_commitment_mode_keyboard(str(participation_id), lang)
    sent = await message.answer(combined, reply_markup=markup)
    family_value = getattr(family, "value", family)
    await state.update_data(
        _cwiz_mid=getattr(sent, "message_id", None),
        commit_pid=str(participation_id),
        commit_family=family_value,
        commit_summary="",
    )


def _family_prompt(base: str, family: str | None) -> str:
    suffix = {
        "SALAWAT": "salawat",
        "DUA": "dua",
        "LAAN": "laan",
    }.get(family or "")
    return f"{base}.{suffix}" if suffix else base


@router.callback_query(F.data.startswith("cmback:"))
async def previous_commitment_step(callback: CallbackQuery, state: FSMContext) -> None:
    target = callback.data.split(":", 1)[1]
    data = await state.get_data()
    lang = _lang_of(callback.message)
    pid = str(data.get("commit_pid") or "")
    family = data.get("commit_family")
    if target == "mode":
        await state.set_state(None)
        text = "\n\n".join((t("commit.explain", lang), _question(t("commit.ask_mode", lang))))
        await _mwiz(
            callback.message, state, text,
            reply_markup=member_commitment_mode_keyboard(pid, lang),
        )
    elif target == "freq":
        await state.set_state(None)
        await _mwiz(
            callback.message, state, _question(t("commit.ask_freq", lang)),
            reply_markup=commitment_freq_keyboard(pid, lang),
        )
    elif target == "times":
        await state.set_state(CommitFlow.entering_times_per_period)
        period = t(_PERIOD_KEY.get(data.get("commit_freq"), "commit.period.day"), lang)
        await _mwiz(
            callback.message, state,
            _question(t(_family_prompt("commit.ask_times_per_period", family), lang, period=period)),
            reply_markup=member_commitment_back_keyboard("freq", lang),
        )
    elif target == "hour":
        await state.set_state(None)
        await _mwiz(
            callback.message, state, _question(t("commit.ask_hour", lang)),
            reply_markup=commitment_hour_keyboard(lang),
        )
    await safe_answer_callback(callback)


# ---- Mode selection ---------------------------------------------------------

@router.callback_query(F.data.startswith("cmode:regular:"))
async def choose_regular(callback: CallbackQuery, state: FSMContext) -> None:
    pid = callback.data.split(":", 2)[2]
    lang = _lang_of(callback.message)
    await safe_clear_inline_keyboard(callback.message)
    await state.update_data(commit_pid=pid, _cwiz_mid=callback.message.message_id)
    await _mwiz(callback.message, state, _question(t("commit.ask_freq", lang)), reply_markup=commitment_freq_keyboard(pid, lang))
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cmode:count:"))
async def choose_count(callback: CallbackQuery, state: FSMContext) -> None:
    pid = callback.data.split(":", 2)[2]
    lang = _lang_of(callback.message)
    await safe_clear_inline_keyboard(callback.message)
    await state.set_state(CommitFlow.entering_count)
    await state.update_data(commit_pid=pid, _cwiz_mid=callback.message.message_id)
    data = await state.get_data()
    await _mwiz(
        callback.message, state,
        _question(t(_family_prompt("commit.ask_count", data.get("commit_family")), lang)),
        reply_markup=member_commitment_back_keyboard("mode", lang),
    )
    await safe_answer_callback(callback)


# ---- COUNT mode -------------------------------------------------------------

@router.message(StateFilter(CommitFlow.entering_count))
async def enter_count(message: Message, state: FSMContext) -> None:
    lang = _lang_of(message)
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        data = await state.get_data()
        question = t(_family_prompt("commit.ask_count", data.get("commit_family")), lang)
        await _mwiz(message, state, _retry_question(t("commit.ask_count_invalid", lang), question),
                    reply_markup=member_commitment_back_keyboard("mode", lang))
        return
    target = int(raw)
    data = await state.get_data()
    pid = data.get("commit_pid")
    async with session_scope() as session:
        await participation_service.set_commitment_count(session, pid, target)
    await state.update_data(_cwiz_mid=None)
    await _mwiz(message, state, t("commit.count_saved", lang, target=target),
                reply_markup=commitment_count_log_keyboard(str(pid), lang))
    await state.set_state(None)


@router.callback_query(F.data.startswith("clog:1:"))
async def log_one(callback: CallbackQuery, state: FSMContext) -> None:
    pid = callback.data.split(":", 2)[2]
    await _apply_log(callback, pid, 1)
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("clogc:"))
async def log_custom(callback: CallbackQuery, state: FSMContext) -> None:
    pid = callback.data.split(":", 1)[1]
    lang = _lang_of(callback.message)
    await state.set_state(CommitFlow.entering_log_amount)
    await state.update_data(commit_pid=pid)
    await callback.message.answer(t("commit.ask_log_amount", lang))
    await safe_answer_callback(callback)


@router.message(StateFilter(CommitFlow.entering_log_amount))
async def enter_log_amount(message: Message, state: FSMContext) -> None:
    lang = _lang_of(message)
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer(t("commit.ask_count_invalid", lang))
        return
    data = await state.get_data()
    pid = data.get("commit_pid")
    await state.set_state(None)
    await _apply_log(message, pid, int(raw))


@router.callback_query(F.data.startswith("cnew:"))
async def new_pledge(callback: CallbackQuery, state: FSMContext) -> None:
    pid = callback.data.split(":", 1)[1]
    lang = _lang_of(callback.message)
    await state.set_state(CommitFlow.entering_count)
    await state.update_data(commit_pid=pid)
    await callback.message.answer(t("commit.ask_count", lang))
    await safe_answer_callback(callback)


async def _apply_log(obj, pid, amount: int) -> None:
    target_msg = obj.message if isinstance(obj, CallbackQuery) else obj
    lang = _lang_of(target_msg)
    async with session_scope() as session:
        result = await participation_service.log_commitment_count(session, pid, amount)
    if result is None:
        return
    done, target, completed = result
    key = "commit.count_completed" if completed else "commit.count_logged"
    await target_msg.answer(
        t(key, lang, done=done, target=target),
        reply_markup=commitment_count_log_keyboard(str(pid), lang),
    )


# ---- REGULAR mode -----------------------------------------------------------

_PERIOD_KEY = {
    ScheduleFreq.DAILY.value: "commit.period.day",
    ScheduleFreq.WEEKLY.value: "commit.period.week",
    ScheduleFreq.MONTHLY.value: "commit.period.month",
}


async def _ask_times_per_period(message: Message, state: FSMContext) -> None:
    lang = _lang_of(message)
    data = await state.get_data()
    freq = data.get("commit_freq")
    await state.set_state(CommitFlow.entering_times_per_period)
    period = t(_PERIOD_KEY.get(freq, "commit.period.day"), lang)
    if freq == ScheduleFreq.WEEKLY.value:
        period = t("commit.period.these_days", lang)
    await _mwiz(
        message, state,
        _question(t(_family_prompt("commit.ask_times_per_period", data.get("commit_family")), lang, period=period)),
        reply_markup=member_commitment_back_keyboard("freq", lang),
    )


@router.callback_query(F.data.startswith("cfreq:"))
async def choose_freq(callback: CallbackQuery, state: FSMContext) -> None:
    _, freq, pid = callback.data.split(":", 2)
    lang = _lang_of(callback.message)
    await safe_clear_inline_keyboard(callback.message)
    await state.update_data(commit_pid=pid, commit_freq=freq)
    # Owner L4 (2026-09-30): WEEKLY first asks which days of the week (multi-select).
    if freq == ScheduleFreq.WEEKLY.value:
        await state.set_state(CommitFlow.choosing_weekdays)
        await state.update_data(commit_weekdays=[])
        await _mwiz(
            callback.message, state, _question(t("commit.ask_weekdays", lang)),
            reply_markup=commitment_weekday_keyboard(pid, set(), lang),
        )
        await safe_answer_callback(callback)
        return
    await _ask_times_per_period(callback.message, state)
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cdow:"), StateFilter(CommitFlow.choosing_weekdays))
async def toggle_weekday(callback: CallbackQuery, state: FSMContext) -> None:
    _, idx, pid = callback.data.split(":", 2)
    lang = _lang_of(callback.message)
    data = await state.get_data()
    selected = set(data.get("commit_weekdays") or [])
    i = int(idx)
    if i in selected:
        selected.discard(i)
    else:
        selected.add(i)
    await state.update_data(commit_weekdays=sorted(selected))
    try:
        await callback.message.edit_reply_markup(
            reply_markup=commitment_weekday_keyboard(pid, selected, lang)
        )
    except Exception:
        pass
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cdowok:"), StateFilter(CommitFlow.choosing_weekdays))
async def confirm_weekdays(callback: CallbackQuery, state: FSMContext) -> None:
    lang = _lang_of(callback.message)
    data = await state.get_data()
    selected = sorted(set(data.get("commit_weekdays") or []))
    if not selected:
        await safe_answer_callback(callback, t("commit.weekdays_need_one", lang), show_alert=True)
        return
    await safe_clear_inline_keyboard(callback.message)
    await _ask_times_per_period(callback.message, state)
    await safe_answer_callback(callback)


@router.message(StateFilter(CommitFlow.entering_times_per_period))
async def enter_times_per_period(message: Message, state: FSMContext) -> None:
    lang = _lang_of(message)
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        data = await state.get_data()
        period = t("commit.period.these_days", lang) if data.get("commit_freq") == ScheduleFreq.WEEKLY.value else t(_PERIOD_KEY.get(data.get("commit_freq"), "commit.period.day"), lang)
        question = t(_family_prompt("commit.ask_times_per_period", data.get("commit_family")), lang, period=period)
        await _mwiz(message, state, _retry_question(t("commit.ask_count_invalid", lang), question),
                    reply_markup=member_commitment_back_keyboard("freq", lang))
        return
    await state.update_data(commit_times=int(raw))
    await state.set_state(None)
    await _mwiz(message, state, _question(t("commit.ask_hour", lang)), reply_markup=commitment_hour_keyboard(lang))


@router.callback_query(F.data.startswith("chour:"))
async def choose_hour(callback: CallbackQuery, state: FSMContext) -> None:
    payload = callback.data.split(":", 1)[1]
    lang = _lang_of(callback.message)
    if payload == "custom":
        await safe_clear_inline_keyboard(callback.message)
        await state.set_state(CommitFlow.entering_custom_time)
        await _mwiz(
            callback.message, state, _question(t("commit.ask_custom_time", lang)),
            reply_markup=member_commitment_back_keyboard("hour", lang),
        )
        await safe_answer_callback(callback)
        return
    await safe_clear_inline_keyboard(callback.message)
    await _save_regular(callback.message, state, int(payload), 0)
    await safe_answer_callback(callback)


@router.message(StateFilter(CommitFlow.entering_custom_time))
async def enter_custom_time(message: Message, state: FSMContext) -> None:
    lang = _lang_of(message)
    parsed = parse_hhmm(message.text or "")
    if parsed is None:
        await _mwiz(message, state, _retry_question(
            t("commit.ask_custom_time_invalid", lang), t("commit.ask_custom_time", lang),
        ), reply_markup=member_commitment_back_keyboard("hour", lang))
        return
    hour, minute = parsed
    await state.set_state(None)
    await _save_regular(message, state, hour, minute)


async def _save_regular(message: Message, state: FSMContext, hour: int, minute: int) -> None:
    lang = _lang_of(message)
    data = await state.get_data()
    pid = data.get("commit_pid")
    freq = data.get("commit_freq")
    times = data.get("commit_times") or 1
    weekdays = None
    if freq == ScheduleFreq.WEEKLY.value:
        sel = sorted(set(data.get("commit_weekdays") or []))
        weekdays = ",".join(str(i) for i in sel) if sel else None
    async with session_scope() as session:
        await participation_service.set_commitment_schedule(
            session, pid, freq=freq, hour=hour, minute=minute,
            times_per_period=times, weekdays=weekdays,
        )
    # delete the last prompt, then send a persistent confirmation + home menu
    prev = (await state.get_data()).get("_cwiz_mid")
    if prev:
        try:
            await message.bot.delete_message(message.chat.id, prev)
        except Exception:
            pass
    await state.update_data(_cwiz_mid=None)
    # Owner (2026-10-01): for WEEKLY the TOTAL = (chosen days) × (times per day).
    # e.g. 4 days × 1 = «۴ مرتبه در هفته»، 4 days × 2 = «۸ مرتبه در هفته».
    if freq == ScheduleFreq.WEEKLY.value:
        days = len([d for d in (data.get("commit_weekdays") or [])])
        display_times = (days or 1) * times
        period = t("commit.period.week", lang)
    else:
        display_times = times
        period = t("commit.period.day", lang)
    await message.answer(
        t("commit.regular_saved", lang, times=display_times, period=period, hour=f"{hour:02d}:{minute:02d}"),
        reply_markup=_home_markup(message),
    )


@router.callback_query(
    F.data.startswith("regular_done:") | F.data.startswith("regular_early_done:")
)
async def confirm_regular_occurrence(callback: CallbackQuery) -> None:
    """Confirm the current scheduled occurrence once, by its owning member."""
    pid = callback.data.split(":", 1)[1]
    is_early = callback.data.startswith("regular_early_done:")
    lang = _lang_of(callback.message)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        participation = await participation_service.get_by_id(session, pid)
        if (
            participation is None
            or participation.user_id != user.id
            or participation.status != ParticipationStatus.ACTIVE
            or participation.commitment_mode != CommitmentMode.REGULAR.value
            or (not is_early and participation.schedule_last_sent_at is None)
            or not participation_matches_bot(participation, callback.message.bot)
        ):
            await safe_answer_callback(callback, t("commit.regular.invalid", lang), show_alert=True)
            return
        if is_early:
            settings = await settings_service.get_or_create(session, user.id)
            try:
                user_tz = ZoneInfo(settings.timezone)
            except (KeyError, ValueError):
                user_tz = ZoneInfo("Asia/Tehran")
            today = datetime.now(timezone.utc).astimezone(user_tz).date()
            sent_today = (
                participation.schedule_last_sent_at is not None
                and participation.schedule_last_sent_at.astimezone(user_tz).date() == today
            )
            if sent_today and await open_contribution_service.has_for_participation_since(
                session, participation.id, participation.schedule_last_sent_at
            ):
                await safe_answer_callback(callback, t("commit.regular.already_done", lang), show_alert=True)
                return
            if not sent_today:
                await participation_service.mark_schedule_sent_now(session, participation.id)
        elif await open_contribution_service.has_for_participation_since(
            session, participation.id, participation.schedule_last_sent_at
        ):
            await safe_answer_callback(callback, t("commit.regular.already_done", lang), show_alert=True)
            return
        khatm = await khatm_service.get_khatm(session, participation.khatm_id)
        if khatm is None:
            await safe_answer_callback(callback, t("commit.regular.invalid", lang), show_alert=True)
            return
        amount = participation.commitment_per_occurrence or 1
        await open_contribution_service.log_contribution(
            session, khatm.id, participation.id, amount, khatm.repetition_target
        )
        # Owner (2026-10-01): thank + invite others into THIS khatm with its link.
        from khatmsaz.bot.handlers.portions import _invite_friends_line
        invite_line = await _invite_friends_line(
            session, khatm, khatm.creator_user_id, platform, lang, bot=callback.message.bot
        )
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(
        t("commit.regular.done_confirmed", lang, count=amount) + (invite_line or "")
    )
    await safe_answer_callback(callback)
