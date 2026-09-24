"""Small, user-facing Telegram command menu for the primary journeys."""

from aiogram import Bot
from aiogram.types import BotCommand

from khatmsaz.modules.identity.models import Platform


USER_COMMANDS = [
    BotCommand(command="start", description="شروع و نمایش منوی اصلی"),
    BotCommand(command="help", description="راهنما و پشتیبانی"),
    BotCommand(command="public_khatms", description="ختم‌های در حال برگزاری"),
    BotCommand(command="my_khatms", description="ختم‌های من (مشارکت‌ها)"),
]


async def install_command_menu(bot: Bot) -> bool:
    """Install Telegram's native command picker; Bale parity is unverified."""
    if getattr(bot, "khatmsaz_platform", None) != Platform.TELEGRAM:
        return False
    await bot.set_my_commands(USER_COMMANDS)
    await bot.set_my_commands(USER_COMMANDS, language_code="fa")
    return True
