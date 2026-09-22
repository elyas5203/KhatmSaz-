"""Creator approve/reject for a PRIVATE khatm's join request
(DOMAIN_MODEL.md §2 Q65-66). The request itself isn't persisted anywhere —
the khatm id and requester's user id are carried through the callback data,
same pattern as the committed-leave approval in `leave.py`.

Like `leave.py`, this fans out to two different people (the requester and
the creator) — each message is built in that recipient's own stored
language, resolved separately.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from khatmsaz.bot.handlers.start import build_join_success_message
from khatmsaz.bot.keyboards import safe_answer_callback, safe_clear_inline_keyboard
from khatmsaz.bot.notify_adapter import get_notify_fn, send_with_keyboard
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import CreatorDisplayMode
from khatmsaz.modules.khatm_workflow import service as workflow_service
from khatmsaz.modules.participation.service import AlreadyParticipatingError
from khatmsaz.modules.settings import service as settings_service

router = Router(name="join_requests")


async def _lang_for_user(session, user_id) -> str:
    settings = await settings_service.get_or_create(session, user_id)
    return settings.language


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        return await _lang_for_user(session, user.id)


@router.callback_query(F.data.startswith("approve_join:"))
async def approve_join(callback: CallbackQuery) -> None:
    _, khatm_id, user_id = callback.data.split(":", 2)

    async with session_scope() as session:
        platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
        actor = await identity_service.find_by_platform(session, platform, str(callback.from_user.id))
        if actor is None:
            lang = await _lang_for(callback.message.chat.id, callback.bot)
            await safe_answer_callback(callback, t("join_requests.account_not_found", lang), show_alert=True)
            return
        creator_lang = await _lang_for_user(session, actor.id)
        try:
            khatm, participation, first_portion, was_waitlisted = await workflow_service.approve_join_request(
                session, khatm_id, user_id, creator_user_id=actor.id
            )
        except PermissionError:
            await safe_answer_callback(callback, t("join_requests.only_creator_can_approve", creator_lang), show_alert=True)
            return
        except AlreadyParticipatingError:
            await safe_clear_inline_keyboard(callback.message)
            await callback.message.answer(t("join_requests.already_member", creator_lang))
            await safe_answer_callback(callback)
            return
        except workflow_service.KhatmUnavailableError:
            await safe_clear_inline_keyboard(callback.message)
            await callback.message.answer(t("join_requests.khatm_not_active", creator_lang))
            await safe_answer_callback(callback)
            return

        requester = await identity_service.find_by_id(session, user_id)
        requester_identities = await identity_service.list_identities_for_user(session, user_id)
        requester_lang = await _lang_for_user(session, user_id)
        display_name = requester.display_name if requester and requester.display_name else t(
            "join.default_display_name", requester_lang
        )
        creator = await identity_service.find_by_id(session, khatm.creator_user_id)
        creator_mode = getattr(khatm, "creator_display_mode", CreatorDisplayMode.FULL_NAME.value)
        if creator_mode == CreatorDisplayMode.ANONYMOUS.value:
            creator_display_name = t("join.creator_display.anonymous", requester_lang)
        elif creator_mode == CreatorDisplayMode.PSEUDONYM.value:
            creator_display_name = getattr(khatm, "creator_pseudonym", None) or t("join.creator_display.anonymous", requester_lang)
        else:
            creator_display_name = creator.display_name if creator and creator.display_name else ""
            if creator_mode == CreatorDisplayMode.FIRST_NAME and creator_display_name:
                creator_display_name = creator_display_name.split()[0]

    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(t("join_requests.approved_creator_side", creator_lang))
    await safe_answer_callback(callback)

    text, keyboard = build_join_success_message(
        khatm, participation, first_portion, was_waitlisted, display_name, creator_display_name, requester_lang
    )
    for identity in requester_identities:
        await send_with_keyboard(identity.platform.value, identity.subject, text, keyboard)


@router.callback_query(F.data.startswith("reject_join:"))
async def reject_join(callback: CallbackQuery) -> None:
    _, khatm_id, user_id = callback.data.split(":", 2)

    async with session_scope() as session:
        khatm = await khatm_service.get_khatm(session, khatm_id)
        platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
        actor = await identity_service.find_by_platform(session, platform, str(callback.from_user.id))
        if khatm is None or actor is None or khatm.creator_user_id != actor.id:
            lang = await _lang_for(callback.message.chat.id, callback.bot)
            await safe_answer_callback(callback, t("join_requests.only_creator_can_reject", lang), show_alert=True)
            return
        creator_lang = await _lang_for_user(session, actor.id)
        requester_identities = await identity_service.list_identities_for_user(session, user_id)
        requester_lang = await _lang_for_user(session, user_id)

    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(t("join_requests.rejected_creator_side", creator_lang))
    await safe_answer_callback(callback)

    notify = get_notify_fn()
    title = khatm.title if khatm else t("join_requests.this_khatm_fallback", requester_lang)
    text = t("join_requests.rejected_requester_side", requester_lang, title=title)
    for identity in requester_identities:
        await notify(identity.platform.value, identity.subject, text)
