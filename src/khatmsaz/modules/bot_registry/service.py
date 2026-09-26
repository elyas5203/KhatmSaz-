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

    if category and category.group == KhatmCategoryGroup.DUA:
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
