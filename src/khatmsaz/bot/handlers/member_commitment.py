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
from khatmsaz.bot.member_scope import participation_matches_bot, member_instance_id
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import KhatmTemplateType
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
        "ZIYARAT": "dua",
        "DUA_ZIYARAT": "dua",
        "LAAN": "laan",
        "QURAN": "quran",
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
    from khatmsaz.modules.share_occurrence import delivery
    from khatmsaz.bot.member_scope import member_instance_id
    lang = _lang_of(message)
    raw = (message.text or "").strip()
    if not raw.isdecimal() or not 0 < int(raw) <= 2147483647:
        await message.answer(t("commit.ask_count_invalid", lang))
        return
    data = await state.get_data()
    platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    try:
        async with session_scope() as session:
            user = await identity_service.resolve_or_provision_user(session, platform, message.from_user.id)
            occurrence = await delivery.prepare_numeric(session, data.get("commit_pid"), int(raw),
                user_id=user.id, bot_instance_id=member_instance_id(message.bot))
            if occurrence is None:
                await message.answer(t("portions.no_capacity_left", lang))
                return
        # Persist allocation first, then deliver; a failed API call retains the
        # exact pages and is retried by the scheduler without making new debt.
        async with session_scope() as session:
            from khatmsaz.modules.share_occurrence import repository
            occurrence = await repository.get(session, occurrence.id)
            part = await participation_service.get_by_id(session, occurrence.participation_id)
            await khatm_service.get_khatm_for_update(session, part.khatm_id)
            await participation_service.repository.get_by_id_for_update(session, part.id)
            occurrence = await repository.get(session, occurrence.id, for_update=True)
            try:
                delivered = await delivery.deliver(session, occurrence)
            except Exception:
                if not session.is_active:
                    raise
                delivered = False
        await state.clear()
        await message.answer("🌱 سهم شما ثبت شد. " + (
            "این رزرو ۷ روز اعتبار دارد؛ پس از خواندن، انجام همین سهم را ثبت کنید."
            if occurrence.reservation_id else "تعهد این سهم تا انجام باقی می‌ماند."
        ) + ("" if delivered or occurrence.delivered_at else "\nارسال محتوا هنوز کامل نشده؛ دوباره تلاش می‌کنیم."))
    except ValueError:
        await message.answer("این مقدار یا برنامه قابل ثبت نیست. عضویت، مقدار سهم و تنظیمات ختم را بررسی کنید.")


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
        from khatmsaz.modules.share_occurrence import repository as shares
        from khatmsaz.modules.participation import repository as memberships
        part = await participation_service.get_by_id(session, pid)
        platform = getattr(target_msg.bot, "khatmsaz_platform", Platform.TELEGRAM)
        user = await identity_service.resolve_or_provision_user(session, platform, target_msg.chat.id)
        if (part is None or part.user_id != user.id or member_instance_id(target_msg.bot) is None
                or not participation_matches_bot(part, target_msg.bot) or amount <= 0):
            await target_msg.answer(t("portions.not_a_member", lang))
            return
        await khatm_service.get_khatm_for_update(session, part.khatm_id)
        part = await memberships.get_by_id_for_update(session, part.id)
        if await shares.has_any(session, part.id):
            await target_msg.answer("برای ثبت انجام، دکمهٔ زیر همان سهم را بزنید. سهم‌ها از «سهم امروز من» در دسترس‌اند.")
            return
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
        participation = await participation_service.get_by_id(session, pid)
        platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        if (participation is None or participation.user_id != user.id
                or member_instance_id(message.bot) is None
                or not participation_matches_bot(participation, message.bot)):
            await state.clear()
            await message.answer(t("portions.not_a_member", lang))
            return
        khatm = await khatm_service.get_khatm(session, participation.khatm_id) if participation else None
        if khatm is not None and khatm.template_type == KhatmTemplateType.QURAN_PAGE and data.get("commit_family") != "QURAN":
            # A stale repetition wizard must not save Salawat settings for Quran.
            from khatmsaz.bot.handlers.portions import start_open_quran_setup
            await state.clear()
            await start_open_quran_setup(message, state, khatm_id=str(khatm.id), lang=lang)
            return
        if khatm is not None and khatm.commitment_policy == "FIXED_DAILY":
            await state.clear()
            await message.answer("مقدار و برنامهٔ روزانهٔ این ختم را سازنده تعیین کرده است؛ فقط ساعت دریافت را از تنظیمات تغییر دهید.")
            return
        if khatm is not None and khatm.template_type == KhatmTemplateType.QURAN_PAGE:
            from khatmsaz.modules.content import service as content
            if times > content.get_quran_total_pages(khatm):
                await message.answer("تعداد صفحات نباید بیشتر از کل صفحات قرآن باشد.")
                return
            await participation_service.set_open_reading_pages_per_day(session, pid, times)
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
    _LOCALIZED_WEEKDAYS = {
        0: "days.saturday", 1: "days.sunday", 2: "days.monday",
        3: "days.tuesday", 4: "days.wednesday", 5: "days.thursday", 6: "days.friday"
    }
    family = data.get("commit_family")
    unit = t("portions.unit.page", lang) if family == "QURAN" else t("commit.unit.salawat", lang) if family == "SALAWAT" else t("commit.unit.dua", lang)
    
    if freq == ScheduleFreq.WEEKLY.value:
        sel = sorted(set(data.get("commit_weekdays") or []))
        days = len(sel)
        weekly_sum = (days or 1) * times
        if sel:
            days_text = "، ".join(t(_LOCALIZED_WEEKDAYS[d], lang) for d in sel)
        else:
            days_text = t("commit.every_day", lang)
    else:
        weekly_sum = times * 7
        days_text = t("commit.every_day", lang)
        
    await message.answer(
        t("commit.regular_saved_detailed", lang, days_text=days_text, hour=f"{hour:02d}:{minute:02d}", times=times, weekly_sum=weekly_sum, unit=unit),
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
        khatm = await khatm_service.get_khatm(session, participation.khatm_id)
        if khatm is None or khatm.template_type in (KhatmTemplateType.QURAN_PAGE, KhatmTemplateType.QURAN_SURAH):
            await safe_answer_callback(callback, t("commit.regular.invalid", lang), show_alert=True)
            return
        from khatmsaz.modules.share_occurrence import repository as shares
        if await shares.has_any(session, participation.id):
            await safe_answer_callback(callback, "برای ثبت انجام، دکمهٔ زیر همان سهم را بزنید؛ این دکمه مربوط به برنامهٔ قدیمی است.", show_alert=True)
            return
        await khatm_service.get_khatm_for_update(session, participation.khatm_id)
        participation = await participation_service.repository.get_by_id_for_update(session, participation.id)
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
        # Thank + invite others into THIS khatm with its direct member-bot link.
        from khatmsaz.bot.handlers.portions import _invite_friends_line
        from khatmsaz.bot.member_copy import completion_text, content_family, share_label
        invite_line = await _invite_friends_line(
            session, khatm, khatm.creator_user_id, platform, lang, bot=callback.message.bot
        )
        family = await content_family(session, khatm)
        confirmed_text = completion_text(
            khatm, family, share_label(family, count=amount, lang=lang),
            invite_line=invite_line, lang=lang,
        )
    try:
        await callback.message.delete()
    except Exception:
        await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(confirmed_text)
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("share_done:"))
async def complete_share(callback: CallbackQuery) -> None:
    from uuid import UUID
    from khatmsaz.modules.share_occurrence import service as shares, repository, delivery
    from khatmsaz.bot.occurrence_adapter import cleanup
    from khatmsaz.bot.member_scope import member_instance_id
    try:
        oid = UUID(callback.data.split(":", 1)[1])
    except ValueError:
        await safe_answer_callback(callback)
        return
    platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
        occurrence = await repository.get(session, oid)
        part = await participation_service.get_by_id(session, occurrence.participation_id) if occurrence else None
        if part is None or part.user_id != user.id or occurrence.bot_instance_id != member_instance_id(callback.message.bot):
            await safe_answer_callback(callback, "این سهم متعلق به شما نیست.", show_alert=True)
            return
        khatm = await khatm_service.get_khatm_for_update(session, part.khatm_id)
        try:
            occurrence, changed = await shares.complete(session, oid, user_id=user.id,
                bot_instance_id=member_instance_id(callback.message.bot), record_progress=delivery.record_progress)
        except shares.OccurrenceAccessError:
            await safe_answer_callback(callback, "این رزرو دیگر معتبر نیست یا ارسال سهم هنوز کامل نشده است.", show_alert=True)
            return
    # Completion has committed before best-effort message cleanup.
    async with session_scope() as session:
        await cleanup(session, part, occurrence)
    await safe_answer_callback(callback, "✅ انجام این سهم ثبت شد." if changed else "این سهم قبلاً ثبت شده است.")
    if changed:
        from khatmsaz.bot.member_copy import completion_text, share_label
        family = occurrence.content_spec.get("family", "salawat")
        lang = occurrence.content_spec.get("language", "fa")
        await callback.message.answer(completion_text(khatm, family,
            share_label(family, count=occurrence.amount, lang=lang), lang=lang))


@router.callback_query(F.data.startswith("legacy_share_done:"))
async def complete_legacy_share(callback: CallbackQuery):
    from uuid import UUID
    from khatmsaz.modules.share_occurrence import service as shares
    from khatmsaz.bot.member_scope import member_instance_id
    try:
        pid = UUID(callback.data.split(":",1)[1])
        async with session_scope() as session:
            platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
            user = await identity_service.resolve_or_provision_user(session, platform, callback.from_user.id)
            changed = await shares.complete_legacy_portion(session, pid, user_id=user.id,
                bot_instance_id=member_instance_id(callback.message.bot))
    except ValueError:
        await safe_answer_callback(callback, "این سهم برای این عضویت قابل ثبت نیست.", show_alert=True)
        return
    await safe_answer_callback(callback, "✅ انجام سهم قبلی ثبت شد." if changed else "این سهم قبلاً ثبت شده است.")
    await safe_clear_inline_keyboard(callback.message)
