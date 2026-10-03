import re

path = 'src/khatmsaz/bot/handlers/portions.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

pattern = r"confirmation = completion_text\(\s*khatm, \"quran\",\s*share_label\(\"quran\", start=completed\.unit_start, end=completed\.unit_end, lang=lang\),\s*invite_line=invite_line, lang=lang,\s*\)"
match = re.search(pattern, content)

if match:
    new_code = """from khatmsaz.bot.member_copy import content_family
    family = await content_family(session, khatm)
    
    # If it's a quantity-based portion, unit_start and unit_end are probably None,
    # but completed.quantity is set.
    if completed.unit_kind.name == "QUANTITY":
        count = completed.quantity
        label = share_label(family, count=count, lang=lang)
    else:
        label = share_label(family, start=completed.unit_start, end=completed.unit_end, lang=lang)
        
    confirmation = completion_text(
        khatm, family,
        label,
        invite_line=invite_line, lang=lang,
    )"""
    content = content[:match.start()] + new_code + content[match.end():]
    with open(path, 'w', encoding='utf-8') as f: f.write(content)
    print("Patched mark_portion_done successfully!")
else:
    print("Pattern not found in portions.py!")
