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
from khatmsaz.bot import invite_links
from khatmsaz.bot.keyboards import safe_answer_callback, safe_clear_inline_keyboard, unpack_join_callback_data, unpack_join_callback_route
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
from khatmsaz.core.bot_registry import get_registry

router = Router(name="join_requests")


async def _lang_for_user(session, user_id) -> str:
    settings = await settings_service.get_or_create(session, user_id)
    return settings.language


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        return await _lang_for_user(session, user.id)


async def _member_bot_for_request(session, packed: str, khatm_id, user_id, fallback_platform: Platform):
    """Resolve the exact route in new callbacks and a safe best effort for old pending ones."""
    route = unpack_join_callback_route(packed)
    registry = get_registry()
    if route is not None:
        route_platform, route_category, route_language = route
        return registry.get_member_bot(Platform(route_platform), route_category, route_language)

    # Backward compatibility for approval buttons created before the route was
    # embedded. A user's sole platform is unambiguous; linked accounts prefer
    # the platform on which the creator clicked the pending request.
    khatm = await khatm_service.get_khatm(session, khatm_id)
    if khatm is None:
        return None
    category = await invite_links.resolve_khatm_category_value(session, khatm)
    language = await _lang_for_user(session, user_id)
    identities = await identity_service.list_identities_for_user(session, user_id)
    platforms = list(dict.fromkeys(identity.platform for identity in identities))
    if fallback_platform in platforms:
        platforms.remove(fallback_platform)
        platforms.insert(0, fallback_platform)
    for platform in platforms:
        candidate = registry.get_member_bot(platform, category, language)
        if candidate is not None:
            return candidate
    return None


@router.callback_query(F.data.startswith("approve_join:"))
async def approve_join(callback: CallbackQuery) -> None:
    packed = callback.data.split(":", 1)[1]
    khatm_id, user_id = unpack_join_callback_data(packed)

    async with session_scope() as session:
        platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
        member_bot = await _member_bot_for_request(session, packed, khatm_id, user_id, platform)
        member_bot_instance_id = getattr(member_bot, "khatmsaz_instance_id", None)
        actor = await identity_service.find_by_platform(session, platform, str(callback.from_user.id))
        if actor is None:
            lang = await _lang_for(callback.message.chat.id, callback.bot)
            await safe_answer_callback(callback, t("join_requests.account_not_found", lang), show_alert=True)
            return
        creator_lang = await _lang_for_user(session, actor.id)
        try:
            khatm, participation, first_portion, was_waitlisted = await workflow_service.approve_join_request(
                session, khatm_id, user_id, creator_user_id=actor.id,
                joined_via_bot_instance_id=member_bot_instance_id,
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
        await send_with_keyboard(
            identity.platform.value, identity.subject, text, keyboard,
            bot_instance_id=participation.joined_via_bot_instance_id,
        )

    # P2: Ask for reminder time for regular commitment khatms (same condition as resume_join_after_registration)
    # The creator is approving asynchronously, so we can't trigger an FSM state for the user.
    # Instead, we send a standalone keyboard that uses the settings handler directly.
    from khatmsaz.modules.khatm.models import KhatmTypeEnum, KhatmTemplateType
    from khatmsaz.modules.notification import service as notification_service
    is_repetition_commitment = (
        khatm.khatm_type == KhatmTypeEnum.COMMITMENT
        and khatm.template_type not in (KhatmTemplateType.QURAN_PAGE, KhatmTemplateType.QURAN_SURAH)
    )
    is_member_choice = getattr(khatm, "commitment_policy", "MEMBER_CHOICE") == "MEMBER_CHOICE"

    needs_reminder = False
    needs_mode_picker = False
    
    is_member_choice = (
        khatm.khatm_type == KhatmTypeEnum.OPEN 
        or (khatm.khatm_type == KhatmTypeEnum.COMMITMENT and getattr(khatm, "commitment_policy", "MEMBER_CHOICE") == "MEMBER_CHOICE")
    )
    
    if khatm.khatm_type in (KhatmTypeEnum.COMMITMENT, KhatmTypeEnum.OPEN):
        if is_member_choice:
            needs_mode_picker = True
        else:
            async with session_scope() as session:
                pref = await notification_service.get_preference(session, participation.id)
                if pref is None:
                    needs_reminder = True
                    
    if needs_mode_picker:
        from khatmsaz.bot.keyboards import member_commitment_mode_keyboard
        prompt_text = "

".join(part for part in (
            t("commit.explain", requester_lang).strip(), 
            "? " + t("commit.ask_mode", requester_lang).strip(),
        ) if part)
        prompt_keyboard = member_commitment_mode_keyboard(str(participation.id), requester_lang)
        for identity in requester_identities:
            await send_with_keyboard(
                identity.platform.value, identity.subject, prompt_text, prompt_keyboard,
                bot_instance_id=participation.joined_via_bot_instance_id,
            )
            
    if needs_reminder:
        from khatmsaz.bot.keyboards import join_delivery_hour_keyboard
        prompt_text = t("join.ask_delivery_hour", requester_lang)
        prompt_keyboard = join_delivery_hour_keyboard(str(participation.id), requester_lang)
        for identity in requester_identities:
            await send_with_keyboard(
                identity.platform.value, identity.subject, prompt_text, prompt_keyboard,
                bot_instance_id=participation.joined_via_bot_instance_id,
            )


@router.callback_query(F.data.startswith("reject_join:"))
async def reject_join(callback: CallbackQuery) -> None:
    packed = callback.data.split(":", 1)[1]
    khatm_id, user_id = unpack_join_callback_data(packed)

    async with session_scope() as session:
        khatm = await khatm_service.get_khatm(session, khatm_id)
        platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
        member_bot = await _member_bot_for_request(session, packed, khatm_id, user_id, platform)
        member_bot_instance_id = getattr(member_bot, "khatmsaz_instance_id", None)
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
        await notify(
            identity.platform.value, identity.subject, text,
            bot_instance_id=member_bot_instance_id,
        )
