import re
path = 'src/khatmsaz/bot/keyboards.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

new_func = '''
def join_delivery_hour_keyboard(participation_id: str, lang: str = "fa") -> InlineKeyboardMarkup:
    labels = {
        7: t("delivery_hour.early_morning", lang),
        9: t("delivery_hour.morning", lang),
        12: t("delivery_hour.noon", lang),
        15: t("delivery_hour.afternoon", lang),
        18: t("delivery_hour.evening", lang),
        21: t("delivery_hour.night", lang),
    }
    rows = [
        [InlineKeyboardButton(text=labels[7], callback_data=f"set_reminder:{participation_id}:7:0"),
         InlineKeyboardButton(text=labels[9], callback_data=f"set_reminder:{participation_id}:9:0")],
        [InlineKeyboardButton(text=labels[12], callback_data=f"set_reminder:{participation_id}:12:0"),
         InlineKeyboardButton(text=labels[15], callback_data=f"set_reminder:{participation_id}:15:0")],
        [InlineKeyboardButton(text=labels[18], callback_data=f"set_reminder:{participation_id}:18:0"),
         InlineKeyboardButton(text=labels[21], callback_data=f"set_reminder:{participation_id}:21:0")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
'''

if 'def join_delivery_hour_keyboard' not in content:
    content += new_func
    with open(path, 'w', encoding='utf-8') as f: f.write(content)
