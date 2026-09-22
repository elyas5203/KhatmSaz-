"""See `models.py` for why this module exists. `KNOWN_SETTINGS` is the
whitelist of keys an admin is allowed to set via `/admin_setting_set` —
this is deliberately a whitelist (not free-form key/value) so a typo in a
key can't silently create a dead, never-read setting; every key here must
correspond to a real place in the code that reads it via `get_int`."""

from sqlalchemy.ext.asyncio import AsyncSession

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
    return {
        key: (int(rows[key]) if key in rows else meta["default"])
        for key, meta in KNOWN_SETTINGS.items()
    }
