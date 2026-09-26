"""Runtime registry of all live Bot instances, built once at startup."""

from __future__ import annotations

from uuid import UUID

from aiogram import Bot

from khatmsaz.modules.bot_registry.models import BotCategory, BotRole
from khatmsaz.modules.identity.models import Platform


class BotRegistry:

    def __init__(self, bots: list[Bot]) -> None:
        self._bots_by_id: dict[UUID, Bot] = {}
        self._creator_bots: dict[Platform, Bot] = {}
        self._member_bots: dict[tuple[Platform, BotCategory, str], Bot] = {}
        self._all: list[Bot] = list(bots)

        for bot in bots:
            iid = getattr(bot, "khatmsaz_instance_id", None)
            if iid:
                self._bots_by_id[iid] = bot

            role = getattr(bot, "khatmsaz_role", None)
            plat = getattr(bot, "khatmsaz_platform", None)

            if role == BotRole.CREATOR and plat:
                self._creator_bots[plat] = bot
            elif role == BotRole.MEMBER and plat:
                cat = getattr(bot, "khatmsaz_category", None)
                lang = getattr(bot, "khatmsaz_language", None)
                if cat and lang:
                    self._member_bots[(plat, cat, lang)] = bot

    def get_creator_bot(self, platform: Platform) -> Bot | None:
        return self._creator_bots.get(platform)

    def get_member_bot(
        self, platform: Platform, category: BotCategory, language: str,
    ) -> Bot | None:
        return self._member_bots.get((platform, category, language))

    def get_by_instance_id(self, instance_id: UUID) -> Bot | None:
        return self._bots_by_id.get(instance_id)

    def all_bots(self) -> list[Bot]:
        return list(self._all)

    def creator_bots(self) -> list[Bot]:
        return list(self._creator_bots.values())

    def member_bots(self) -> list[Bot]:
        return list(self._member_bots.values())


_registry: BotRegistry | None = None


def set_registry(registry: BotRegistry) -> None:
    global _registry
    _registry = registry


def get_registry() -> BotRegistry:
    if _registry is None:
        raise RuntimeError("BotRegistry not initialized — call set_registry() at startup")
    return _registry
