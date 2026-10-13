"""See `models.py` for why this module exists. `KNOWN_SETTINGS` is the
whitelist of keys an admin is allowed to set via `/admin_setting_set` —
this is deliberately a whitelist (not free-form key/value) so a typo in a
key can't silently create a dead, never-read setting; every key here must
correspond to a real place in the code that reads it via `get_int`."""

from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlparse
import re

from khatmsaz.modules.system_settings import repository

KNOWN_SETTINGS: dict[str, dict] = {
    "default_reminder_hour": {
        "default": 9, "min": 0, "max": 23,
        "label_fa": "ساعت پیش‌فرض یادآوری (برای کسی که هنوز خودش تنظیم نکرده)",
    },
    "inactivity_days": {
        "default": 30, "min": 1, "max": 365,
        "label_fa": "تعداد روز عدم‌فعالیت قبل از واگذاری سهم قرآن به یار ذخیره",
    },
    "broadcast_telegram_free_count": {"default": 0, "min": 0, "max": 1000, "label_fa": "تعداد پیام رایگان تلگرام (منسوخ)"},
    "broadcast_telegram_price_toman": {"default": 50_000, "min": 0, "max": 100_000_000, "label_fa": "هزینه هر بسته ۱۰۰۰ نفری پیام تلگرام"},
    "broadcast_bale_free_count": {"default": 0, "min": 0, "max": 1000, "label_fa": "تعداد پیام رایگان بله (منسوخ)"},
    "broadcast_bale_price_toman": {"default": 50_000, "min": 0, "max": 100_000_000, "label_fa": "هزینه هر بسته ۱۰۰۰ نفری پیام بله"},
    "broadcast_sms_free_count": {"default": 0, "min": 0, "max": 1000, "label_fa": "تعداد پیامک رایگان (منسوخ)"},
    "broadcast_sms_price_toman": {"default": 100_000, "min": 0, "max": 100_000_000, "label_fa": "هزینه هر بسته ۱۰۰۰ نفری پیامک"},
}

KNOWN_STRING_SETTINGS = {
    "panel_logo_url",
    "intro_image_quran",
    "intro_image_salawat",
    "intro_image_dua_ziyarat",
    "intro_image_laan",
    "intro_image_khutbah",
    "custom_khatm_admin_phone",
}


async def get_int(session: AsyncSession, key: str) -> int:
    if key not in KNOWN_SETTINGS:
        raise ValueError(f"unknown system setting: {key}")
    raw = await repository.get(session, key)
    if raw is None:
        return KNOWN_SETTINGS[key]["default"]
    try:
        return int(raw)
    except ValueError:
        return KNOWN_SETTINGS[key]["default"]


async def set_int(session: AsyncSession, key: str, value: int) -> None:
    if key not in KNOWN_SETTINGS:
        raise ValueError(f"unknown system setting: {key}")
    bounds = KNOWN_SETTINGS[key]
    if not bounds["min"] <= value <= bounds["max"]:
        raise ValueError(f"{key} must be between {bounds['min']} and {bounds['max']}")
    await repository.set(session, key, str(value))


async def list_current(session: AsyncSession) -> dict[str, int]:
    rows = {row.key: row.value for row in await repository.list_all(session)}
    result: dict[str, int] = {}
    for key, meta in KNOWN_SETTINGS.items():
        if key in rows:
            try:
                result[key] = int(rows[key])
            except (TypeError, ValueError):
                result[key] = meta["default"]
        else:
            result[key] = meta["default"]
    return result


list_all = list_current


async def get_str(session: AsyncSession, key: str, default: str = "") -> str:
    if key not in KNOWN_STRING_SETTINGS:
        raise ValueError(f"unknown string system setting: {key}")
    return (await repository.get(session, key)) or default


async def set_str(session: AsyncSession, key: str, value: str) -> None:
    if key not in KNOWN_STRING_SETTINGS:
        raise ValueError(f"unknown string system setting: {key}")
    normalized = value.strip()
    if key == "custom_khatm_admin_phone":
        compact = re.sub(r"[\s()-]", "", normalized)
        if compact and not re.fullmatch(r"\+?\d{8,15}", compact):
            raise ValueError("custom khatm admin phone must be a valid phone number")
        await repository.set(session, key, compact)
        return
    if normalized:
        parsed = urlparse(normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"{key} must be an HTTP(S) URL")
        if len(normalized) > 500:
            raise ValueError(f"{key} is too long")
    await repository.set(session, key, normalized)
