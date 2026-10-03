import re

path = 'src/khatmsaz/bot/handlers/start.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

# We want to replace everything from "is_repetition_commitment = (" 
# down to "AskDeliveryHour.entering_hour)"
pattern = r"is_repetition_commitment = \(.*?(?=await state\.set_state\(AskDeliveryHour\.entering_hour\))"
match = re.search(pattern, content, re.DOTALL)
if match:
    new_block = """is_member_choice = (
        khatm.khatm_type == KhatmTypeEnum.OPEN 
        or (khatm.khatm_type == KhatmTypeEnum.COMMITMENT and getattr(khatm, "commitment_policy", "MEMBER_CHOICE") == "MEMBER_CHOICE")
    )
    
    if state is not None and is_fresh_join and is_member_choice:
        from khatmsaz.bot.handlers.member_commitment import start_commitment_mode_picker
        family = pending_category_group if 'pending_category_group' in locals() else None
        await start_commitment_mode_picker(
            message, state, participation.id, lang, summary=text, family=family
        )
    elif (
        state is not None and is_fresh_join
        and await notification_service.get_preference(session, participation.id) is None
    ):
        """
    content = content[:match.start()] + new_block + content[match.end():]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched successfully!")
else:
    print("Pattern not found!")
