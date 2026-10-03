import re

# 1. Update i18n
i18n_path = 'src/khatmsaz/i18n/__init__.py'
with open(i18n_path, 'r', encoding='utf-8') as f:
    i18n_content = f.read()

new_keys = '''
    "create_khatm.ask_daily_quran": {
        "fa": "??? ???? ?????? ?????? ???? 2 ????",
        "ar": "?? ???? ???? ?????? ???? 2 ????",
        "en": "How many pages daily? (e.g. 2)"
    },
    "create_khatm.ask_daily_salawat": {
        "fa": "??? ????? ?? ??? ?????? ???? 100 ?????",
        "ar": "?? ????? ?? ?????? ???? 100",
        "en": "How many salawat daily? (e.g. 100)"
    },
    "create_khatm.ask_daily_laan": {
        "fa": "??? ??? ?? ??? ???? ?????? ???? 50 ???",
        "ar": "?? ??? ?? ?????? ???? 50",
        "en": "How many la'n daily? (e.g. 50)"
    },
    "create_khatm.ask_daily_dua": {
        "fa": "??? ??? ??? ??? ?? ??? ?????? ??? ???? 1 ???",
        "ar": "?? ??? ???? ??? ??????? ???? 1",
        "en": "How many times daily? (e.g. 1)"
    },
    "days.monday": {"fa": "??????", "ar": "???????", "en": "Mon"},
    "days.tuesday": {"fa": "???????", "ar": "????????", "en": "Tue"},
    "days.wednesday": {"fa": "????????", "ar": "????????", "en": "Wed"},
    "days.thursday": {"fa": "????????", "ar": "??????", "en": "Thu"},
    "days.friday": {"fa": "????", "ar": "??????", "en": "Fri"},
    "days.saturday": {"fa": "????", "ar": "?????", "en": "Sat"},
    "days.sunday": {"fa": "??????", "ar": "?????", "en": "Sun"},
'''
if 'create_khatm.ask_daily_quran' not in i18n_content:
    i18n_content = i18n_content.replace('_STRINGS: dict[str, dict[str, str]] = {', '_STRINGS: dict[str, dict[str, str]] = {\n' + new_keys)
    with open(i18n_path, 'w', encoding='utf-8') as f:
        f.write(i18n_content)

# 2. Update create_khatm.py
create_khatm = 'src/khatmsaz/bot/handlers/create_khatm.py'
with open(create_khatm, 'r', encoding='utf-8') as f:
    ck = f.read()

old_block = '''        unit = (
            t("create_khatm.unit.salawat", lang)
            if data.get("category_group") == KhatmCategoryGroup.SALAWAT.value
            else (t("create_khatm.unit.time", lang) if data.get("template_type") == KhatmTemplateType.SALAWAT.value else t("create_khatm.unit.page", lang))
        )
        await _wiz(
            callback.message, state, t("create_khatm.ask_fixed_daily_amount", lang, unit=unit),
            reply_markup=create_wizard_back_keyboard(lang),
        )'''

new_block = '''        tt = data.get("template_type", "")
        cg = data.get("category_group", "")
        if tt == "QURAN":
            ask_key = "create_khatm.ask_daily_quran"
        elif tt == "SALAWAT" or cg == "SALAWAT":
            ask_key = "create_khatm.ask_daily_salawat"
        elif tt == "LAAN":
            ask_key = "create_khatm.ask_daily_laan"
        else:
            ask_key = "create_khatm.ask_daily_dua"
            
        await _wiz(
            callback.message, state, t(ask_key, lang),
            reply_markup=create_wizard_back_keyboard(lang),
        )'''
ck = ck.replace(old_block, new_block)
with open(create_khatm, 'w', encoding='utf-8') as f:
    f.write(ck)
print('done')
