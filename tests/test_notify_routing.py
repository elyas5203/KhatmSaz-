"""Regression: notifications must go from the correct bot per platform.

A user can have both a Telegram and a Bale identity while joining a khatm
through a single-platform member bot. `notify(..., bot_instance_id=...)`
previously used that member bot for EVERY platform, so the other-platform
identity got a message sent from the wrong-platform bot (which silently
fails — no reminder). Now the member bot is used only for its own platform;
other platforms fall back to that platform's creator bot."""
import pytest

from khatmsaz.bot import notify_adapter
from khatmsaz.core import bot_registry as reg
from khatmsaz.modules.identity.models import Platform


class FakeBot:
    def __init__(self, platform, instance_id=None, label=""):
        self.khatmsaz_platform = platform
        self.khatmsaz_instance_id = instance_id
        self.label = label
        self.sent = []

    async def send_message(self, chat_id, text):
        self.sent.append((chat_id, text))


class FakeRegistry:
    def __init__(self, tg_member, tg_creator, bale_creator):
        self._by_id = {tg_member.khatmsaz_instance_id: tg_member}
        self._creator = {Platform.TELEGRAM: tg_creator, Platform.BALE: bale_creator}

    def get_by_instance_id(self, iid):
        return self._by_id.get(iid)

    def get_creator_bot(self, platform):
        return self._creator.get(platform)


@pytest.mark.asyncio
async def test_notify_does_not_route_member_bot_to_other_platform(monkeypatch):
    tg_member = FakeBot(Platform.TELEGRAM, instance_id="inst-tg", label="tg-member")
    tg_creator = FakeBot(Platform.TELEGRAM, label="tg-creator")
    bale_creator = FakeBot(Platform.BALE, label="bale-creator")
    monkeypatch.setattr(reg, "_registry", FakeRegistry(tg_member, tg_creator, bale_creator))

    notify = notify_adapter.build_notify_fn({})

    # Telegram identity + the member-bot instance → delivered from the member bot.
    await notify("TELEGRAM", "111", "سلام", bot_instance_id="inst-tg")
    assert tg_member.sent == [(111, "سلام")]

    # Bale identity with the SAME (Telegram) instance id → must NOT use the
    # Telegram member bot; falls back to the Bale creator bot.
    await notify("BALE", "222", "سلام", bot_instance_id="inst-tg")
    assert bale_creator.sent == [(222, "سلام")]
    assert all(cid != 222 for cid, _ in tg_member.sent), "message leaked to wrong-platform member bot"
