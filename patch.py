import re

with open('src/khatmsaz/bot/member_copy.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''    res = (
        "با سلام و احترام 🌱\\n\\n"
        f"لطفاً {share} از ختم «{escape(khatm.title)}» را تا پایان {deadline_text} {action} بفرمایید "
        "و پس از انجام، روی دکمهٔ «✅ قرائت انجام شد» بزنید.\\n\\n"
        "اگر امروز فرصت کافی ندارید، می‌توانید از دوستان یا خانواده خود برای انجام این سهم کمک بگیرید "
        "تا برنامهٔ امروز ختم کامل بماند.\\n\\n"
        "در پناه حق تعالی باشید."
    )
    if family == "quran" and audio_enabled:
        res += "\\n\\n💡 برای خاموش کردن دریافت صوت قرآن، می‌توانید به بخش تنظیمات ربات مراجعه کنید."
    return res'''

content = re.sub(r'    res = \([\s\S]*?    \)\s*return res', target, content)

with open('src/khatmsaz/bot/member_copy.py', 'w', encoding='utf-8') as f:
    f.write(content)
