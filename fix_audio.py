path = 'src/khatmsaz/modules/settings/models.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

content = content.replace('quran_audio_enabled: Mapped[bool] = mapped_column(Boolean, default=False)', 'quran_audio_enabled: Mapped[bool] = mapped_column(Boolean, default=True)')

with open(path, 'w', encoding='utf-8') as f: f.write(content)
