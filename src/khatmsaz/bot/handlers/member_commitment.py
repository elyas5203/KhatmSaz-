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

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message

from khatmsaz.bot.keyboards import (
    commitment_count_log_keyboard,
    commitment_freq_keyboard,
    commitment_hour_keyboard,
    member_commitment_mode_keyboard,
    member_menu_keyboard,
    main_menu_keyboard,
    safe_answer_callback,
    safe_clear_inline_keyboard,
)
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.bot_registry.models import BotRole
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.participation.commitment import ScheduleFreq, parse_hhmm

router = Router(name="member_commitment")


class CommitFlow(StatesGroup):
    entering_count = State()           # COUNT: pledge amount (also re-pledge)
    entering_log_amount = State()      # COUNT: custom log amount
    entering_times_per_period = State()  # REGULAR: how many times per day/week/month
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
    """Ephemeral prompt: delete the previous bot prompt AND the member's own typed
    message, then send the new one — «هی پاک بشه چون قاطی می‌کنن». Best-effort."""
    data = await state.get_data()
    prev = data.get("_cwiz_mid")
    if prev:
        try:
            await message.bot.delete_message(message.chat.id, prev)
        except Exception:
            pass
    if getattr(getattr(message, "from_user", None), "is_bot", True) is False:
        try:
            await message.bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
    sent = await message.answer(text, reply_markup=reply_markup)
    await state.update_data(_cwiz_mid=getattr(sent, "message_id", None))
    return sent


async def start_commitment_mode_picker(message: Message, participation_id, lang: str) -> None:
    """Kick off the mode picker for a freshly-joined commitment member."""
    await message.answer(t("commit.explain", lang))
    sent = await message.answer(
        t("commit.ask_mode", lang),
        reply_markup=member_commitment_mode_keyboard(str(participation_id), lang),
    )
    # seed the ephemeral tracker so the first real step deletes this prompt too


# ---- Mode selection ---------------------------------------------------------

@router.callback_query(F.data.startswith("cmode:regular:"))
async def choose_regular(callback: CallbackQuery, state: FSMContext) -> None:
    pid = callback.data.split(":", 2)[2]
    lang = _lang_of(callback.message)
    await safe_clear_inline_keyboard(callback.message)
    await state.update_data(commit_pid=pid, _cwiz_mid=callback.message.message_id)
    await _mwiz(callback.message, state, t("commit.ask_freq", lang), reply_markup=commitment_freq_keyboard(pid, lang))
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cmode:count:"))
async def choose_count(callback: CallbackQuery, state: FSMContext) -> None:
    pid = callback.data.split(":", 2)[2]
    lang = _lang_of(callback.message)
    await safe_clear_inline_keyboard(callback.message)
    await state.set_state(CommitFlow.entering_count)
    await state.update_data(commit_pid=pid, _cwiz_mid=callback.message.message_id)
    await _mwiz(callback.message, state, t("commit.ask_count", lang))
    await safe_answer_callback(callback)


# ---- COUNT mode -------------------------------------------------------------

@router.message(StateFilter(CommitFlow.entering_count))
async def enter_count(message: Message, state: FSMContext) -> None:
    lang = _lang_of(message)
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await _mwiz(message, state, t("commit.ask_count_invalid", lang))
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


@router.callback_query(F.data.startswith("cfreq:"))
async def choose_freq(callback: CallbackQuery, state: FSMContext) -> None:
    _, freq, pid = callback.data.split(":", 2)
    lang = _lang_of(callback.message)
    await safe_clear_inline_keyboard(callback.message)
    await state.update_data(commit_pid=pid, commit_freq=freq)
    await state.set_state(CommitFlow.entering_times_per_period)
    period = t(_PERIOD_KEY.get(freq, "commit.period.day"), lang)
    await _mwiz(callback.message, state, t("commit.ask_times_per_period", lang, period=period))
    await safe_answer_callback(callback)


@router.message(StateFilter(CommitFlow.entering_times_per_period))
async def enter_times_per_period(message: Message, state: FSMContext) -> None:
    lang = _lang_of(message)
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await _mwiz(message, state, t("commit.ask_count_invalid", lang))
        return
    await state.update_data(commit_times=int(raw))
    await state.set_state(None)
    await _mwiz(message, state, t("commit.ask_hour", lang), reply_markup=commitment_hour_keyboard(lang))


@router.callback_query(F.data.startswith("chour:"))
async def choose_hour(callback: CallbackQuery, state: FSMContext) -> None:
    payload = callback.data.split(":", 1)[1]
    lang = _lang_of(callback.message)
    if payload == "custom":
        await safe_clear_inline_keyboard(callback.message)
        await state.set_state(CommitFlow.entering_custom_time)
        await _mwiz(callback.message, state, t("commit.ask_custom_time", lang))
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
        await _mwiz(message, state, t("commit.ask_custom_time_invalid", lang))
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
    async with session_scope() as session:
        await participation_service.set_commitment_schedule(
            session, pid, freq=freq, hour=hour, minute=minute, times_per_period=times
        )
    # delete the last prompt, then send a persistent confirmation + home menu
    prev = (await state.get_data()).get("_cwiz_mid")
    if prev:
        try:
            await message.bot.delete_message(message.chat.id, prev)
        except Exception:
            pass
    await state.update_data(_cwiz_mid=None)
    period = t(_PERIOD_KEY.get(freq, "commit.period.day"), lang)
    await message.answer(
        t("commit.regular_saved", lang, times=times, period=period, hour=f"{hour:02d}:{minute:02d}"),
        reply_markup=_home_markup(message),
    )
