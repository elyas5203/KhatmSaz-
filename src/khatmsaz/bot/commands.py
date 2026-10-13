"""Small, user-facing Telegram command menu for the primary journeys."""

from aiogram import Bot
from aiogram.types import BotCommand

from khatmsaz.modules.bot_registry.models import BotRole
from khatmsaz.modules.identity.models import Platform


USER_COMMANDS = [
    BotCommand(command="start", description="شروع و نمایش منوی اصلی"),
    BotCommand(command="help", description="راهنما و پشتیبانی"),
    BotCommand(command="public_khatms", description="ختم‌های در حال برگزاری"),
    BotCommand(command="my_khatms", description="ختم‌های من (مشارکت‌ها)"),
]

ADMIN_COMMANDS = [
    BotCommand(command="start", description="داشبورد مدیریت مرکزی"),
    BotCommand(command="receipts", description="کارتابل فیش‌های واریزی"),
    BotCommand(command="laan", description="ختم‌های لعن در انتظار"),
    BotCommand(command="broadcasts", description="پیام‌های همگانی در انتظار"),
    BotCommand(command="status", description="وضعیت سرور و خدمات"),
    BotCommand(command="logs", description="مشاهده لاگ‌های سامانه"),
    BotCommand(command="errors", description="مشاهده خطاهای اخیر"),
    BotCommand(command="admin_app", description="ورود به پنل تحت وب"),
]


async def install_command_menu(bot: Bot) -> bool:
    """Install Telegram's native command picker; Bale parity is unverified."""
    if getattr(bot, "khatmsaz_platform", None) != Platform.TELEGRAM:
        return False
    role = getattr(bot, "khatmsaz_role", None)
    cmds = ADMIN_COMMANDS if role == BotRole.ADMIN else USER_COMMANDS
    await bot.set_my_commands(cmds)
    await bot.set_my_commands(cmds, language_code="fa")
    return True
