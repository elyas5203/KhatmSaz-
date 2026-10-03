import re
path = 'src/khatmsaz/modules/reminder_engine/service.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

# I will just replace all instances of:
# deadline=getattr(khatm, "daily_deadline_hour", None), lang=user_settings.language,
# with:
# deadline=getattr(khatm, "daily_deadline_hour", None), lang=user_settings.language, audio_enabled=user_settings.quran_audio_enabled

content = content.replace('deadline=getattr(khatm, "daily_deadline_hour", None), lang=user_settings.language,', 'deadline=getattr(khatm, "daily_deadline_hour", None), lang=user_settings.language, audio_enabled=user_settings.quran_audio_enabled,')

with open(path, 'w', encoding='utf-8') as f: f.write(content)
