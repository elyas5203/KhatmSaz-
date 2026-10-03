import re
path = 'src/khatmsaz/modules/reminder_engine/service.py'
with open(path, 'r', encoding='utf-8') as f: content = f.read()

# 1. deliver_due_next_portions (the one that calls reminder_text directly)
old_1 = '''        text = reminder_text(
            khatm, "quran",
            share_label("quran", start=next_portion.unit_start, end=next_portion.unit_end, lang=user_settings.language),
            deadline=getattr(khatm, "daily_deadline_hour", None), lang=user_settings.language,
        )'''
new_1 = '''        text = reminder_text(
            khatm, "quran",
            share_label("quran", start=next_portion.unit_start, end=next_portion.unit_end, lang=user_settings.language),
            deadline=getattr(khatm, "daily_deadline_hour", None), lang=user_settings.language, audio_enabled=user_settings.quran_audio_enabled
        )'''
content = content.replace(old_1, new_1)

# 2. _maybe_send_staged_reminder signature
content = content.replace('heading: str, locale: str', 'heading: str, locale: str, audio_enabled: bool = False')

# 3. _maybe_send_staged_reminder body
old_3 = '''    text = heading + "\\n\\n" + reminder_text(
        khatm, "quran",
        share_label("quran", start=portion.unit_start, end=portion.unit_end, lang=locale),
        deadline=getattr(khatm, "daily_deadline_hour", None), lang=locale,
    )'''
new_3 = '''    text = heading + "\\n\\n" + reminder_text(
        khatm, "quran",
        share_label("quran", start=portion.unit_start, end=portion.unit_end, lang=locale),
        deadline=getattr(khatm, "daily_deadline_hour", None), lang=locale, audio_enabled=audio_enabled
    )'''
content = content.replace(old_3, new_3)

# 4. _maybe_send_staged_reminder calls in _send_daily_digest
old_4a = '''            await _maybe_send_staged_reminder(
                session, notify, participation, khatm, portion,
                NotificationKind.SECOND_REMINDER, "OO_OU^OUO O_U^U. dYO", user_settings.language,
            )'''
new_4a = '''            await _maybe_send_staged_reminder(
                session, notify, participation, khatm, portion,
                NotificationKind.SECOND_REMINDER, "OO_OU^OUO O_U^U. dYO", user_settings.language, audio_enabled=user_settings.quran_audio_enabled
            )'''
content = content.replace(old_4a, new_4a)

old_4b = '''            await _maybe_send_staged_reminder(
                session, notify, participation, khatm, portion,
                NotificationKind.FINAL_REMINDER, "OO'O_O O U+UO UOUO U,O"U, O O U.UU,O ?", user_settings.language,
            )'''
new_4b = '''            await _maybe_send_staged_reminder(
                session, notify, participation, khatm, portion,
                NotificationKind.FINAL_REMINDER, "OO'O_O O U+UO UOUO U,O"U, O O U.UU,O ?", user_settings.language, audio_enabled=user_settings.quran_audio_enabled
            )'''
content = content.replace(old_4b, new_4b)

# 5. deliver_due_next_portions inside P7 2-hour followup
old_5 = '''                            text = "OO_OU^OUO O U+OO U. O3UU. ?3\\n\\n" + reminder_text(
                                khatm, "quran",
                                share_label("quran", start=latest_portion.unit_start, end=latest_portion.unit_end, lang=user_settings.language),
                                deadline=getattr(khatm, "daily_deadline_hour", None), lang=user_settings.language,
                            )'''
new_5 = '''                            text = "OO_OU^OUO O U+OO U. O3UU. ?3\\n\\n" + reminder_text(
                                khatm, "quran",
                                share_label("quran", start=latest_portion.unit_start, end=latest_portion.unit_end, lang=user_settings.language),
                                deadline=getattr(khatm, "daily_deadline_hour", None), lang=user_settings.language, audio_enabled=user_settings.quran_audio_enabled
                            )'''
content = content.replace(old_5, new_5)


with open(path, 'w', encoding='utf-8') as f: f.write(content)
