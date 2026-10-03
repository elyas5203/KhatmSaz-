import re
path = 'src/khatmsaz/modules/reminder_engine/service.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

# Replace all reminder_text calls inside reminder_engine if they don't have audio_enabled
def replacer(match):
    m = match.group(0)
    if 'audio_enabled' in m: return m
    return m.replace(')', ', audio_enabled=user_settings.quran_audio_enabled)')

# For the regular ones that have user_settings in scope
content = re.sub(r'reminder_text\(\s*khatm,\s*"quran",\s*share_label\([^)]+\),\s*deadline=[^,]+,\s*lang=user_settings\.language,\s*\)', replacer, content, flags=re.MULTILINE)

# For _maybe_send_staged_reminder
if 'locale: str, audio_enabled: bool' not in content:
    content = content.replace('heading: str, locale: str', 'heading: str, locale: str, audio_enabled: bool = False')

# inside _maybe_send_staged_reminder
content = re.sub(r'reminder_text\(\s*khatm,\s*"quran",\s*share_label\([^)]+\),\s*deadline=[^,]+,\s*lang=locale,\s*\)', 
                 lambda m: m.group(0).replace(')', ', audio_enabled=audio_enabled)'), content, flags=re.MULTILINE)

# calls to _maybe_send_staged_reminder
content = re.sub(r'(_maybe_send_staged_reminder\(\s*session,\s*notify,\s*participation,\s*khatm,\s*portion,\s*NotificationKind.[A-Z_]+,\s*"[^"]+",\s*user_settings\.language),\s*\)',
                 lambda m: m.group(1) + ', audio_enabled=user_settings.quran_audio_enabled\n            )', content, flags=re.MULTILINE)

with open(path, 'w', encoding='utf-8') as f: f.write(content)
