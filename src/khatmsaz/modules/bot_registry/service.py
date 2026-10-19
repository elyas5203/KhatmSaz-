from __future__ import annotations

import logging
from uuid import UUID

from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.config import get_settings
from khatmsaz.modules.khatm.models import Khatm, KhatmTemplateType
from khatmsaz.modules.khatm_category.models import KhatmCategory, KhatmCategoryGroup

from .models import BotCategory, BotInstance, BotRole
from . import repository

logger = logging.getLogger(__name__)

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = get_settings().bot_token_encryption_key
        if not key:
            raise RuntimeError(
                "BOT_TOKEN_ENCRYPTION_KEY not set — cannot encrypt/decrypt bot tokens"
            )
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet


def encrypt_token(raw_token: str) -> str:
    return _get_fernet().encrypt(raw_token.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    return _get_fernet().decrypt(encrypted.encode()).decode()


def resolve_bot_category(
    khatm: Khatm,
    category: KhatmCategory | None = None,
) -> BotCategory:
    if khatm.template_type in (
        KhatmTemplateType.QURAN_PAGE,
        KhatmTemplateType.QURAN_SURAH,
        KhatmTemplateType.SURAH,
    ):
        return BotCategory.QURAN

    if category and category.group == KhatmCategoryGroup.LAAN:
        return BotCategory.LAAN

    if khatm.template_type in (KhatmTemplateType.DUA, KhatmTemplateType.ZIYARAT):
        return BotCategory.DUA_ZIYARAT

    if category and category.group in (KhatmCategoryGroup.DUA, KhatmCategoryGroup.KHUTBAH):
        return BotCategory.DUA_ZIYARAT

    return BotCategory.SALAWAT


async def list_configured_member_bots(
    session: AsyncSession,
) -> list[BotInstance]:
    return await repository.list_active_members(session)


async def list_all_instances(session: AsyncSession) -> list[BotInstance]:
    return await repository.list_all(session)


async def get_instance(
    session: AsyncSession, instance_id: UUID,
) -> BotInstance | None:
    return await repository.get_by_id(session, instance_id)


async def set_intro_image(
    session: AsyncSession, instance_id: UUID, intro_image_url: str | None,
) -> None:
    """R2: admin sets a bot's intro image (URL or Telegram file_id)."""
    instance = await repository.get_by_id(session, instance_id)
    if instance is None:
        return
    instance.intro_image_url = (intro_image_url or None)
    await session.flush()


async def get_intro_image_for_category(
    session: AsyncSession, category: str, *, platform: str | None = None, language: str | None = None,
) -> str | None:
    """R2: the intro image to show for a khatm of this member-bot category.

    Prefers an exact platform+language match, then any bot of that category that
    has an image set. Returns None if none configured (caller falls back to a
    text-only caption)."""
    from khatmsaz.modules.system_settings import service as system_settings_service

    shared_key = {
        BotCategory.QURAN.value: "intro_image_quran",
        BotCategory.SALAWAT.value: "intro_image_salawat",
        BotCategory.DUA_ZIYARAT.value: "intro_image_dua_ziyarat",
        BotCategory.LAAN.value: "intro_image_laan",
        BotCategory.KHUTBAH.value: "intro_image_khutbah",
    }.get(category)
    if shared_key:
        shared = await system_settings_service.get_str(session, shared_key)
        if shared:
            return shared
    candidates = [
        b for b in await repository.list_all(session)
        if b.bot_role == BotRole.MEMBER.value and b.category == category and b.intro_image_url
    ]
    if not candidates:
        return None
    if platform is not None:
        exact = [b for b in candidates if b.platform == platform and (language is None or b.language == language)]
        if exact:
            return exact[0].intro_image_url
    return candidates[0].intro_image_url


async def set_bot_token(
    session: AsyncSession,
    instance_id: UUID,
    raw_token: str,
    username: str,
) -> None:
    encrypted = encrypt_token(raw_token) if raw_token else ""
    await repository.set_token(session, instance_id, encrypted, username)


async def toggle_bot_active(
    session: AsyncSession,
    instance_id: UUID,
    is_active: bool,
) -> None:
    await repository.toggle_active(session, instance_id, is_active)


async def sync_creator_from_env(session: AsyncSession) -> None:
    settings = get_settings()
    pairs = []
    if settings.telegram_bot_token:
        pairs.append(("TELEGRAM", settings.telegram_bot_token, settings.telegram_bot_username))
    if settings.bale_bot_token:
        pairs.append(("BALE", settings.bale_bot_token, getattr(settings, "bale_bot_username", "")))

    for platform, token, username in pairs:
        existing = await repository.get_by_slot(
            session, platform, BotRole.CREATOR, None, None,
        )
        if existing:
            encrypted = encrypt_token(token)
            await repository.set_token(session, existing.id, encrypted, username)
        else:
            logger.info("Creator bot slot for %s not found in DB — skipping sync", platform)


async def get_decrypted_token(instance: BotInstance) -> str | None:
    if not instance.token_encrypted:
        return None
    try:
        return decrypt_token(instance.token_encrypted)
    except Exception:
        logger.exception("Failed to decrypt token for bot %s", instance.id)
        return None


async def ping_bot_instance(instance: BotInstance, timeout_seconds: float = 4.0) -> dict:
    """Test live connectivity for a BotInstance using getMe() against Telegram or Bale API."""
    import asyncio
    import time
    from khatmsaz.bot.telegram.client import build_telegram_bot
    from khatmsaz.bot.bale.client import build_bale_bot

    if not instance.token_encrypted:
        return {
            "ok": False,
            "error": "توکن در سیستم ثبت نشده است.",
            "latency_ms": None,
            "username": instance.username,
        }

    token = await get_decrypted_token(instance)
    if not token:
        return {
            "ok": False,
            "error": "خطا در رمزگشایی توکن ربات.",
            "latency_ms": None,
            "username": instance.username,
        }

    start = time.perf_counter()
    bot = None
    try:
        if instance.platform == "BALE":
            bot = build_bale_bot(token)
        else:
            bot = build_telegram_bot(token)

        me = await asyncio.wait_for(bot.get_me(), timeout=timeout_seconds)
        latency_ms = round((time.perf_counter() - start) * 1000)
        return {
            "ok": True,
            "latency_ms": latency_ms,
            "username": me.username or instance.username,
            "display_name": me.first_name or instance.display_name,
            "bot_id": me.id,
            "error": None,
        }
    except asyncio.TimeoutError:
        return {
            "ok": False,
            "error": f"مهلت زمان پاسخ‌دهی (Timeout {int(timeout_seconds)} ثانیه) به پایان رسید.",
            "latency_ms": None,
            "username": instance.username,
        }
    except Exception as exc:
        err_msg = str(exc)
        if "Unauthorized" in err_msg:
            clean_err = "توکن ربات نامعتبر است (Unauthorized)."
        else:
            clean_err = f"خطای اتصال: {err_msg[:120]}"
        return {
            "ok": False,
            "error": clean_err,
            "latency_ms": None,
            "username": instance.username,
        }
    finally:
        if bot and hasattr(bot, "session") and hasattr(bot.session, "close"):
            try:
                await bot.session.close()
            except Exception:
                pass


async def ping_all_instances(session: AsyncSession, timeout_seconds: float = 4.0) -> list[dict]:
    """Test live connectivity for all configured bots concurrently."""
    instances = await repository.list_all(session)
    configured = [inst for inst in instances if inst.token_encrypted]
    if not configured:
        return []

    import asyncio

    async def _ping_one(inst: BotInstance) -> dict:
        res = await ping_bot_instance(inst, timeout_seconds=timeout_seconds)
        res["id"] = str(inst.id)
        res["name"] = inst.display_name
        res["platform"] = inst.platform
        res["bot_role"] = inst.bot_role
        res["category"] = inst.category
        res["language"] = inst.language
        return res

    results = await asyncio.gather(*[_ping_one(inst) for inst in configured], return_exceptions=True)
    out = []
    for r in results:
        if isinstance(r, dict):
            out.append(r)
        else:
            out.append({"ok": False, "error": str(r)})
    return out

