import re
path = 'src/khatmsaz/bot/handlers/start.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

# Replace any return of a keyboard with just None for the welcome message
content = re.sub(
    r'return text, contribute_keyboard\(str\(khatm\.id\), lang\)',
    r'return text, None',
    content
)
content = re.sub(
    r'return text, portion_done_keyboard\(str\(khatm\.id\), allow_snooze=bool\(khatm\.allow_snooze\), lang=lang\)',
    r'return text, None',
    content
)
content = re.sub(
    r'return text, commitment_quantity_keyboard\(str\(khatm\.id\), lang\)',
    r'return text, None',
    content
)
content = re.sub(
    r'return text, \(contribute_keyboard\(str\(khatm\.id\), lang\) if quran_join_button else None\)',
    r'return text, None',
    content
)

with open(path, 'w', encoding='utf-8') as f: f.write(content)
