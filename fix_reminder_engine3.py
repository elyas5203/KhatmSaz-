import re
path = 'src/khatmsaz/modules/reminder_engine/service.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

# Replace the remaining reminder_text calls for quran
content = re.sub(r'reminder_text\(\s*khatm,\s*"quran",\s*share_label\([^)]+\),\s*deadline=[^,]+,\s*lang=user_settings\.language,\s*\)', 
                 lambda m: m.group(0).replace(')', ', audio_enabled=user_settings.quran_audio_enabled)'), content, flags=re.MULTILINE)

with open(path, 'w', encoding='utf-8') as f: f.write(content)
