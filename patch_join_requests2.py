import re

path = 'src/khatmsaz/bot/handlers/join_requests.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

pattern = r"(needs_reminder = False\s*if not was_waitlisted.*?)(?=if needs_reminder:)"
match = re.search(pattern, content, re.DOTALL)

if match:
    new_code = """needs_reminder = False
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
        prompt_text = "\n\n".join(part for part in (
            t("commit.explain", requester_lang).strip(), 
            "? " + t("commit.ask_mode", requester_lang).strip(),
        ) if part)
        prompt_keyboard = member_commitment_mode_keyboard(str(participation.id), requester_lang)
        for identity in requester_identities:
            await send_with_keyboard(
                identity.platform.value, identity.subject, prompt_text, prompt_keyboard,
                bot_instance_id=participation.joined_via_bot_instance_id,
            )
            
    """
    content = content[:match.start()] + new_code + content[match.end():]
    with open(path, 'w', encoding='utf-8') as f: f.write(content)
    print("Patched join_requests.py successfully!")
else:
    print("Pattern not found!")
