"""R11/N2 (owner 2026-09-28): member picks HOW they commit to a commitment khatm.

The creator sets only the khatm TOTAL (R5). Each member then chooses one of two
personal commitment modes, with the fewest possible questions:

  • REGULAR — freq (daily/weekly/monthly) → day (weekly/monthly) → hour → how
    many each time. The reminder engine delivers at that local time.
  • COUNT   — a number they pledge, then a button to log progress; on completion
    they can pledge a fresh count (R12).

Entry point `start_commitment_mode_picker` is called from the join flow
(`start.resume_join_after_registration`) right after a member joins a COMMITMENT
khatm, replacing the old "ask delivery hour" step for that case.
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
    member_commitment_mode_keyboard,
    commitment_weekday_keyboard,
    delivery_hour_keyboard,
    member_menu_keyboard,
    main_menu_keyboard,
    safe_answer_callback,
    safe_clear_inline_keyboard,
)
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.bot_registry.models import BotRole
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.participation.commitment import ScheduleFreq

router = Router(name="member_commitment")


class CommitFlow(StatesGroup):
    entering_count = State()          # COUNT: pledge amount (also R12 re-pledge)
    entering_log_amount = State()     # COUNT: custom log amount
    entering_monthday = State()       # REGULAR monthly: day-of-month
    entering_per_occurrence = State()  # REGULAR: how many each occurrence


def _lang_of(obj) -> str:
    bot = obj.bot
    if getattr(bot, "khatmsaz_role", BotRole.CREATOR) == BotRole.MEMBER:
        return getattr(bot, "khatmsaz_language", "fa")
    return "fa"


def _home_markup(obj):
    bot = obj.bot
    lang = _lang_of(obj)
    if getattr(bot, "khatmsaz_role", BotRole.CREATOR) == BotRole.MEMBER:
        return member_menu_keyboard(lang)
    return main_menu_keyboard(lang)


async def start_commitment_mode_picker(message: Message, participation_id, lang: str) -> None:
    """Kick off the mode picker for a freshly-joined commitment member."""
    await message.answer(t("commit.explain", lang))
    await message.answer(
        t("commit.ask_mode", lang),
        reply_markup=member_commitment_mode_keyboard(str(participation_id), lang),
    )


# ---- Mode selection ---------------------------------------------------------

@router.callback_query(F.data.startswith("cmode:regular:"))
async def choose_regular(callback: CallbackQuery, state: FSMContext) -> None:
    pid = callback.data.split(":", 2)[2]
    lang = _lang_of(callback.message)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(
        t("commit.ask_freq", lang), reply_markup=commitment_freq_keyboard(pid, lang)
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cmode:count:"))
async def choose_count(callback: CallbackQuery, state: FSMContext) -> None:
    pid = callback.data.split(":", 2)[2]
    lang = _lang_of(callback.message)
    await safe_clear_inline_keyboard(callback.message)
    await state.set_state(CommitFlow.entering_count)
    await state.update_data(commit_pid=pid)
    await callback.message.answer(t("commit.ask_count", lang))
    await safe_answer_callback(callback)


# ---- COUNT mode -------------------------------------------------------------

@router.message(StateFilter(CommitFlow.entering_count))
async def enter_count(message: Message, state: FSMContext) -> None:
    lang = _lang_of(message)
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer(t("commit.ask_count_invalid", lang))
        return
    target = int(raw)
    data = await state.get_data()
    pid = data.get("commit_pid")
    async with session_scope() as session:
        await participation_service.set_commitment_count(session, pid, target)
    await state.clear()
    await message.answer(
        t("commit.count_saved", lang, target=target),
        reply_markup=commitment_count_log_keyboard(str(pid), lang),
    )


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
    await state.clear()
    await _apply_log(message, pid, int(raw))


@router.callback_query(F.data.startswith("cnew:"))
async def new_pledge(callback: CallbackQuery, state: FSMContext) -> None:
    """R12: after finishing (or any time), pledge a fresh count."""
    pid = callback.data.split(":", 1)[1]
    lang = _lang_of(callback.message)
    await state.set_state(CommitFlow.entering_count)
    await state.update_data(commit_pid=pid)
    await callback.message.answer(t("commit.ask_count", lang))
    await safe_answer_callback(callback)


async def _apply_log(obj, pid, amount: int) -> None:
    lang = _lang_of(obj.message if isinstance(obj, CallbackQuery) else obj)
    target_msg = obj.message if isinstance(obj, CallbackQuery) else obj
    async with session_scope() as session:
        result = await participation_service.log_commitment_count(session, pid, amount)
    if result is None:
        return
    done, target, completed = result
    if completed:
        await target_msg.answer(
            t("commit.count_completed", lang, target=target),
            reply_markup=commitment_count_log_keyboard(str(pid), lang),
        )
    else:
        await target_msg.answer(
            t("commit.count_logged", lang, done=done, target=target),
            reply_markup=commitment_count_log_keyboard(str(pid), lang),
        )


# ---- REGULAR mode -----------------------------------------------------------

@router.callback_query(F.data.startswith("cfreq:"))
async def choose_freq(callback: CallbackQuery, state: FSMContext) -> None:
    _, freq, pid = callback.data.split(":", 2)
    lang = _lang_of(callback.message)
    await safe_clear_inline_keyboard(callback.message)
    await state.update_data(commit_pid=pid, commit_freq=freq, commit_anchor=None)
    if freq == ScheduleFreq.WEEKLY.value:
        await callback.message.answer(
            t("commit.ask_weekday", lang), reply_markup=commitment_weekday_keyboard(pid, lang)
        )
    elif freq == ScheduleFreq.MONTHLY.value:
        await state.set_state(CommitFlow.entering_monthday)
        await callback.message.answer(t("commit.ask_monthday", lang))
    else:  # DAILY
        await state.set_state(CommitFlow.entering_per_occurrence)
        await callback.message.answer(t("commit.ask_per_occurrence", lang))
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cdow:"))
async def choose_weekday(callback: CallbackQuery, state: FSMContext) -> None:
    _, dow, pid = callback.data.split(":", 2)
    lang = _lang_of(callback.message)
    await safe_clear_inline_keyboard(callback.message)
    await state.update_data(commit_pid=pid, commit_anchor=int(dow))
    await state.set_state(CommitFlow.entering_per_occurrence)
    await callback.message.answer(t("commit.ask_per_occurrence", lang))
    await safe_answer_callback(callback)


@router.message(StateFilter(CommitFlow.entering_monthday))
async def enter_monthday(message: Message, state: FSMContext) -> None:
    lang = _lang_of(message)
    raw = (message.text or "").strip()
    if not raw.isdigit() or not (1 <= int(raw) <= 31):
        await message.answer(t("commit.ask_monthday_invalid", lang))
        return
    await state.update_data(commit_anchor=int(raw))
    await state.set_state(CommitFlow.entering_per_occurrence)
    await message.answer(t("commit.ask_per_occurrence", lang))


@router.message(StateFilter(CommitFlow.entering_per_occurrence))
async def enter_per_occurrence(message: Message, state: FSMContext) -> None:
    lang = _lang_of(message)
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer(t("commit.ask_count_invalid", lang))
        return
    await state.update_data(commit_per_occurrence=int(raw))
    # last question: what hour to remind
    await message.answer(
        t("commit.ask_hour", lang), reply_markup=delivery_hour_keyboard("chour", lang)
    )


@router.callback_query(F.data.startswith("chour:"))
async def choose_hour(callback: CallbackQuery, state: FSMContext) -> None:
    hour = int(callback.data.split(":", 1)[1])
    lang = _lang_of(callback.message)
    data = await state.get_data()
    pid = data.get("commit_pid")
    freq = data.get("commit_freq")
    anchor = data.get("commit_anchor")
    per_occ = data.get("commit_per_occurrence") or 1
    await safe_clear_inline_keyboard(callback.message)
    async with session_scope() as session:
        await participation_service.set_commitment_schedule(
            session, pid, freq=freq, anchor=anchor, hour=hour, per_occurrence=per_occ
        )
    await state.clear()
    await callback.message.answer(t("commit.regular_saved", lang), reply_markup=_home_markup(callback.message))
    await safe_answer_callback(callback)
