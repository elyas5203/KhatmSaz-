"""Creator-controlled resolution for repeated missed Quran commitments.

Deprecated (2026-09-21): see `resolve_creator_decision`'s docstring — the
underlying missed-portion/emergency-pool feature was removed."""

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings import service as settings_service

router = Router(name="creator_decisions")


async def _lang_for(chat_id, bot) -> str:
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, chat_id)
        settings = await settings_service.get_or_create(session, user.id)
        return settings.language


@router.message(Command("khatm_decision"))
async def resolve_creator_decision(message: Message, command: CommandObject) -> None:
    """Owner decision (2026-09-21): the missed-portion/emergency-pool system
    this command used to manage was removed entirely — a missed portion no
    longer notifies anyone or needs a creator decision; the participant
    simply gets it the next day they're ready. Kept as a short, harmless
    stub instead of deleting the command outright, since a creator might
    still have the old instructions saved somewhere."""
    lang = await _lang_for(message.chat.id, message.bot)
    await message.answer(t("creator_decisions.no_longer_available", lang))
