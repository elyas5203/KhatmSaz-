"""Small, user-facing Telegram command menu for the primary journeys."""

from aiogram import Bot
from aiogram.types import BotCommand

from khatmsaz.modules.identity.models import Platform


USER_COMMANDS = [
    BotCommand(command="start", description="شروع و نمایش منوی اصلی"),
    BotCommand(command="help", description="راهنمای کامل و مرحله‌به‌مرحله"),
    BotCommand(command="new_khatm", description="ساخت ختم جدید"),
    BotCommand(command="my_khatms", description="دیدن ختم‌های من"),
    BotCommand(command="report", description="گزارش شخصی من"),
    BotCommand(command="public_khatms", description="ختم‌های عمومی قابل عضویت"),
    BotCommand(command="wallet", description="کیف پول و شارژ"),
    BotCommand(command="profile", description="ویرایش مشخصات شخصی"),
    BotCommand(command="verify_phone", description="تأیید شماره برای ساخت ختم"),
    BotCommand(command="change_phone", description="تغییر امن شماره با حفظ سوابق"),
    BotCommand(command="creator_app", description="باز کردن مینی‌اپ سازنده"),
]


async def install_command_menu(bot: Bot) -> bool:
    """Install Telegram's native command picker; Bale parity is unverified."""
    if getattr(bot, "khatmsaz_platform", None) != Platform.TELEGRAM:
        return False
    await bot.set_my_commands(USER_COMMANDS)
    await bot.set_my_commands(USER_COMMANDS, language_code="fa")
    return True
