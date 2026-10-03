import re
path = 'src/khatmsaz/bot/handlers/portions.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

content = content.replace('await message.answer(\"\\\\n\".join(lines), reply_markup=contribute_keyboard(khatm_id, lang))',
                          'await message.answer(\"\\\\n\".join(lines), reply_markup=home_keyboard_for_bot(message.bot, lang))')

content = content.replace('reply_markup=home_keyboard_for_bot(callback.message.bot, lang) if reached else contribute_keyboard(str(khatm.id), lang),',
                          'reply_markup=home_keyboard_for_bot(callback.message.bot, lang),')

with open(path, 'w', encoding='utf-8') as f: f.write(content)
