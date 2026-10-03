import re

path = 'src/khatmsaz/bot/handlers/portions.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

pattern = r"if \(\s*khatm is not None and khatm\.template_type == KhatmTemplateType\.QURAN_PAGE\s*and participation is not None and not participation\.is_committed\s*and participation\.open_reading_pages_per_day is None\s*\):\s*await start_open_quran_setup\(callback\.message, state, khatm_id=khatm_id, lang=lang\)\s*await safe_answer_callback\(callback\)\s*return\s*if \(\s*khatm is not None and khatm\.khatm_type == KhatmTypeEnum\.COMMITMENT \s*and khatm\.template_type not in \(KhatmTemplateType\.QURAN_PAGE, KhatmTemplateType\.QURAN_SURAH\)\s*and participation is not None\s*and getattr\(participation, \"commitment_mode\", None\) is None\s*\):"
match = re.search(pattern, content)
if match:
    new_code = """# V2 Redesign: Any OPEN khatm, or any MEMBER-CHOICE COMMITMENT khatm, 
    # goes to the Mode Picker if mode is not set.
    is_member_choice = (
        khatm.khatm_type == KhatmTypeEnum.OPEN 
        or (khatm.khatm_type == KhatmTypeEnum.COMMITMENT and getattr(khatm, "commitment_policy", "MEMBER_CHOICE") == "MEMBER_CHOICE")
    )
    if (
        khatm is not None and participation is not None 
        and is_member_choice 
        and getattr(participation, "commitment_mode", None) is None
    ):"""
    content = content[:match.start()] + new_code + content[match.end():]
    with open(path, 'w', encoding='utf-8') as f: f.write(content)
    print("Patched portions.py contribute logic!")
else:
    print("Could not match the block.")
