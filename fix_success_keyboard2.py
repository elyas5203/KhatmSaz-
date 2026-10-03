path = 'src/khatmsaz/bot/handlers/portions.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

content = content.replace('reply_markup=contribute_keyboard(khatm_id, lang)', 'reply_markup=home_keyboard_for_bot(message.bot, lang)')

with open(path, 'w', encoding='utf-8') as f: f.write(content)
