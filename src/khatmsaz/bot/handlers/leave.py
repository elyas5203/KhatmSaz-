"""Leaving a khatm. A quick-pick reason is captured first (DOMAIN_MODEL.md
§3 Q98 — for later churn analysis, never shown to the creator).

**Committed participants need creator approval to leave** (user's explicit
decision, 2026-09-16 — see DECISIONS.md): the request goes to the creator
with approve/reject buttons instead of leaving immediately. A non-committed
participant (OPEN khatm, or still-waitlisted in a capacity-limited one)
leaves right away — there's no commitment to protect. No new DB state is
needed for the pending request: the participation id + reason code are
carried through the approve/reject callback data itself.

If a committed leave is approved, the next person in the waiting list (if
any) is promoted and notified (DEC-PY-0010) — this is the one place that
actually exercises `khatm_workflow.leave_khatm`'s promotion path.

Every message here is localized to its *recipient's own* stored language —
a Persian-speaking creator and an English-speaking member on the same
khatm should each read the notification in their own language, so
`_lang_for_user` resolves per user id rather than sharing one `lang`
across everyone involved in a single flow.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from khatmsaz.bot.keyboards import leave_reason_keyboard, main_menu_keyboard, safe_answer_callback, safe_clear_inline_keyboard
from khatmsaz.bot.notify_adapter import get_notify_fn, send_with_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm_workflow import service as workflow_service
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.settings import service as settings_service

router = Router(name="leave")


async def _lang_for_user(session, user_id) -> str:
    settings = await settings_service.get_or_create(session, user_id)
    return settings.language


async def _lang_for(chat_id, bot) -> str:
    from khatmsaz.modules.identity.models import Platform

    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        return await _lang_for_user(session, user.id)


@router.callback_query(F.data.startswith("leave_ask:"))
async def ask_leave_reason(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    participation_id = callback.data.split(":", 1)[1]
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(
        t("leave.ask_reason", lang),
        reply_markup=leave_reason_keyboard(participation_id),
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("leave_reason:"))
async def leave_reason_chosen(callback: CallbackQuery) -> None:
    _, participation_id, reason = callback.data.split(":", 2)

    async with session_scope() as session:
        participation = await participation_service.get_by_id(session, participation_id)
        if participation is None:
            lang = await _lang_for(callback.message.chat.id, callback.bot)
            await safe_answer_callback(callback, t("leave.membership_not_found", lang), show_alert=True)
            return

        requester_lang = await _lang_for_user(session, participation.user_id)

        if not participation.is_committed:
            await _do_leave(session, callback, participation_id, reason, requester_lang=requester_lang)
            return

        # Committed: ask the creator first instead of leaving immediately.
        khatm = await khatm_service.get_khatm(session, participation.khatm_id)
        requester = await identity_service.find_by_id(session, participation.user_id)
        creator_identities = await identity_service.list_identities_for_user(session, khatm.creator_user_id)
        creator_lang = await _lang_for_user(session, khatm.creator_user_id)
        requester_name = requester.display_name if requester and requester.display_name else t(
            "leave.default_member_name", creator_lang
        )

    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(
        t("leave.requester_waiting_for_creator", requester_lang),
        reply_markup=main_menu_keyboard(requester_lang),
    )
    await safe_answer_callback(callback)

    text = t("leave.creator_notify", creator_lang, name=requester_name, title=khatm.title)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("leave.approve_button", creator_lang), callback_data=f"approve_leave:{participation_id}:{reason}"),
                InlineKeyboardButton(text=t("leave.reject_button", creator_lang), callback_data=f"reject_leave:{participation_id}"),
            ]
        ]
    )
    for identity in creator_identities:
        await send_with_keyboard(identity.platform.value, identity.subject, text, keyboard)


@router.callback_query(F.data.startswith("approve_leave:"))
async def approve_leave(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    _, participation_id, reason = callback.data.split(":", 2)
    async with session_scope() as session:
        participation = await participation_service.get_by_id(session, participation_id)
        if participation is None:
            await safe_answer_callback(callback, t("leave.membership_not_found", lang), show_alert=True)
            return
        requester_identities = await identity_service.list_identities_for_user(session, participation.user_id)
        requester_lang = await _lang_for_user(session, participation.user_id)
        await _do_leave(session, callback, participation_id, reason, notify_requester=False, requester_lang=requester_lang)

    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(t("leave.approved_creator_side", lang))
    await safe_answer_callback(callback)

    notify = get_notify_fn()
    for identity in requester_identities:
        await notify(identity.platform.value, identity.subject, t("leave.approved_requester_side", requester_lang))


@router.callback_query(F.data.startswith("reject_leave:"))
async def reject_leave(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.message.chat.id, callback.bot)
    participation_id = callback.data.split(":", 1)[1]
    async with session_scope() as session:
        participation = await participation_service.get_by_id(session, participation_id)
        if participation is None:
            await safe_answer_callback(callback, t("leave.membership_not_found", lang), show_alert=True)
            return
        requester_identities = await identity_service.list_identities_for_user(session, participation.user_id)
        requester_lang = await _lang_for_user(session, participation.user_id)

    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(t("leave.rejected_creator_side", lang))
    await safe_answer_callback(callback)

    notify = get_notify_fn()
    for identity in requester_identities:
        await notify(identity.platform.value, identity.subject, t("leave.rejected_requester_side", requester_lang))


async def _do_leave(
    session, callback: CallbackQuery, participation_id: str, reason: str, *,
    notify_requester: bool = True, requester_lang: str = "fa",
) -> None:
    khatm = None
    participation = await participation_service.get_by_id(session, participation_id)
    if participation is not None:
        khatm = await khatm_service.get_khatm(session, participation.khatm_id)

    promoted_participation, promoted_portion = await workflow_service.leave_khatm(
        session, participation_id, reason=reason
    )

    promoted_identities = []
    promoted_lang = "fa"
    if promoted_participation is not None:
        promoted_identities = await identity_service.list_identities_for_user(session, promoted_participation.user_id)
        promoted_lang = await _lang_for_user(session, promoted_participation.user_id)

    if notify_requester:
        await safe_clear_inline_keyboard(callback.message)
        await callback.message.answer(
            t("leave.left_khatm", requester_lang, title=khatm.title if khatm else ""),
            reply_markup=main_menu_keyboard(requester_lang),
        )
        await safe_answer_callback(callback)

    if promoted_participation is not None:
        notify = get_notify_fn()
        text = t("leave.promoted_notice", promoted_lang, title=khatm.title)
        if promoted_portion is not None:
            text += t("leave.promoted_portion_line", promoted_lang, start=promoted_portion.unit_start, end=promoted_portion.unit_end)
        for identity in promoted_identities:
            await notify(identity.platform.value, identity.subject, text)
