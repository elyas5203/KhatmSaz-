import re
path = 'src/khatmsaz/modules/reminder_engine/service.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

content = content.replace('audio_enabled=user_settings.quran_audio_enabled, audio_enabled=user_settings.quran_audio_enabled', 'audio_enabled=user_settings.quran_audio_enabled')

with open(path, 'w', encoding='utf-8') as f: f.write(content)
