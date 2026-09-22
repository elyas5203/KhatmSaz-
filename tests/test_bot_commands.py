import pytest

from khatmsaz.bot.commands import USER_COMMANDS, install_command_menu
from khatmsaz.modules.identity.models import Platform


class FakeBot:
    def __init__(self, platform):
        self.khatmsaz_platform = platform
        self.calls = []

    async def set_my_commands(self, commands, **kwargs):
        self.calls.append((commands, kwargs))


def test_command_menu_has_unique_realistic_commands():
    names = [item.command for item in USER_COMMANDS]
    assert len(names) == len(set(names))
    assert {"start", "help", "new_khatm", "my_khatms", "verify_phone"} <= set(names)
    assert all(1 <= len(item.description) <= 256 for item in USER_COMMANDS)


@pytest.mark.asyncio
async def test_command_menu_installs_default_and_persian_for_telegram():
    bot = FakeBot(Platform.TELEGRAM)
    assert await install_command_menu(bot) is True
    assert len(bot.calls) == 2
    assert bot.calls[0] == (USER_COMMANDS, {})
    assert bot.calls[1] == (USER_COMMANDS, {"language_code": "fa"})


@pytest.mark.asyncio
async def test_command_menu_skips_unverified_bale_api_parity():
    bot = FakeBot(Platform.BALE)
    assert await install_command_menu(bot) is False
    assert bot.calls == []
