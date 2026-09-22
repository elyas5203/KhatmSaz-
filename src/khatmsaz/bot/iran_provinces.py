"""The 31 official Iranian provinces (ostan) — stable, government-recognized
list, safe to hard-code (unlike a full province→city dataset, which is large
and error-prone to reconstruct from memory — see DOMAIN_MODEL.md's
registration flow and DECISIONS.md DEC-PY-0015 for why city is free text
instead of a second picklist).
"""

IRAN_PROVINCES: list[str] = [
    "آذربایجان شرقی",
    "آذربایجان غربی",
    "اردبیل",
    "اصفهان",
    "البرز",
    "ایلام",
    "بوشهر",
    "تهران",
    "چهارمحال و بختیاری",
    "خراسان جنوبی",
    "خراسان رضوی",
    "خراسان شمالی",
    "خوزستان",
    "زنجان",
    "سمنان",
    "سیستان و بلوچستان",
    "فارس",
    "قزوین",
    "قم",
    "کردستان",
    "کرمان",
    "کرمانشاه",
    "کهگیلویه و بویراحمد",
    "گلستان",
    "گیلان",
    "لرستان",
    "مازندران",
    "مرکزی",
    "هرمزگان",
    "همدان",
    "یزد",
]

OUTSIDE_IRAN = "خارج از ایران"

# Display-only localized labels. The canonical value saved in PostgreSQL is
# always the Persian item at the same index, so changing the UI language can
# never split reports into three spellings of the same province.
IRAN_PROVINCE_LABELS: dict[str, list[str]] = {
    "fa": IRAN_PROVINCES,
    "ar": [
        "أذربيجان الشرقية", "أذربيجان الغربية", "أردبيل", "أصفهان",
        "البرز", "إيلام", "بوشهر", "طهران", "جهارمحال وبختياري",
        "خراسان الجنوبية", "خراسان الرضوية", "خراسان الشمالية", "خوزستان",
        "زنجان", "سمنان", "سيستان وبلوشستان", "فارس", "قزوين", "قم",
        "كردستان", "كرمان", "كرمانشاه", "كهكيلويه وبوير أحمد", "كلستان",
        "غيلان", "لرستان", "مازندران", "مركزي", "هرمزغان", "همدان", "يزد",
    ],
    "en": [
        "East Azerbaijan", "West Azerbaijan", "Ardabil", "Isfahan", "Alborz",
        "Ilam", "Bushehr", "Tehran", "Chaharmahal and Bakhtiari",
        "South Khorasan", "Razavi Khorasan", "North Khorasan", "Khuzestan",
        "Zanjan", "Semnan", "Sistan and Baluchestan", "Fars", "Qazvin", "Qom",
        "Kurdistan", "Kerman", "Kermanshah", "Kohgiluyeh and Boyer-Ahmad",
        "Golestan", "Gilan", "Lorestan", "Mazandaran", "Markazi", "Hormozgan",
        "Hamadan", "Yazd",
    ],
}


def province_labels(language: str) -> list[str]:
    """Localized labels in the exact canonical `IRAN_PROVINCES` order."""
    return IRAN_PROVINCE_LABELS.get(language, IRAN_PROVINCES)
