import re

path = 'src/khatmsaz/bot/handlers/join_requests.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

# Replace the needs_reminder logic
pattern = r"needs_reminder = False\s*if not was_waitlisted and khatm\.khatm_type in \(KhatmTypeEnum\.COMMITMENT, KhatmTypeEnum\.OPEN\):\s*if is_repetition_commitment and is_member_choice:\s*pass # Mode picker handles this\s*else:\s*async with session_scope\(\) as session:\s*pref = await notification_service\.get_preference\(session, participation\.id\)\s*if pref is None:\s*needs_reminder = True"
match = re.search(pattern, content)
if match:
    new_code = """# V2 Redesign: If this is an approval for a waitlisted user,
    # it is effectively their fresh join. They were never asked for their mode/time.
    needs_reminder = False
    needs_mode_picker = False
    
    if khatm.khatm_type in (KhatmTypeEnum.COMMITMENT, KhatmTypeEnum.OPEN):
        if is_member_choice:
            needs_mode_picker = True
        else:
            async with session_scope() as session:
                pref = await notification_service.get_preference(session, participation.id)
                if pref is None:
                    needs_reminder = True
                    
    # Note: If it needs mode picker, we send an inline keyboard to start the mode picker
    """
    # Wait! If it's member choice, we need to send the mode picker keyboard to them!
    print("Found the block. Need to think about how to trigger mode picker asynchronously.")
else:
    print("Pattern not found in join_requests.py!")
