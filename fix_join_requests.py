import re
path = 'src/khatmsaz/bot/handlers/join_requests.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

old_block = '''    text, keyboard = build_join_success_message(
        khatm, participation, first_portion, was_waitlisted, display_name, creator_display_name, requester_lang
    )
    for identity in requester_identities:
        await send_with_keyboard(
            identity.platform.value, identity.subject, text, keyboard,
            bot_instance_id=participation.joined_via_bot_instance_id,
        )'''

new_block = '''    text, keyboard = build_join_success_message(
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
    if not was_waitlisted and khatm.khatm_type in (KhatmTypeEnum.COMMITMENT, KhatmTypeEnum.OPEN):
        if is_repetition_commitment and is_member_choice:
            pass # Mode picker handles this
        else:
            async with session_scope() as session:
                pref = await notification_service.get_preference(session, participation.id)
                if pref is None:
                    needs_reminder = True

    if needs_reminder:
        from khatmsaz.bot.keyboards import join_delivery_hour_keyboard
        prompt_text = t("join.ask_delivery_hour", requester_lang)
        prompt_keyboard = join_delivery_hour_keyboard(str(participation.id), requester_lang)
        for identity in requester_identities:
            await send_with_keyboard(
                identity.platform.value, identity.subject, prompt_text, prompt_keyboard,
                bot_instance_id=participation.joined_via_bot_instance_id,
            )'''

content = content.replace(old_block, new_block)

with open(path, 'w', encoding='utf-8') as f: f.write(content)
