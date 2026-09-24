with open('src/khatmsaz/bot/commands.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

import re
text = "".join(lines)
text = re.sub(
    r'USER_COMMANDS = \[.*?\]',
    'USER_COMMANDS = [\n    BotCommand(command="start", description="شروع و نمایش منوی اصلی"),\n    BotCommand(command="help", description="راهنما و پشتیبانی"),\n    BotCommand(command="public_khatms", description="ختم‌های در حال برگزاری"),\n    BotCommand(command="my_khatms", description="ختم‌های من (مشارکت‌ها)"),\n]',
    text,
    flags=re.DOTALL
)

with open('src/khatmsaz/bot/commands.py', 'w', encoding='utf-8') as f:
    f.write(text)
