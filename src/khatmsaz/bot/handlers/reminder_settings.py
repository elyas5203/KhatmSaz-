"""Small participant-facing reminder preference command."""

from aiogram import F, Router
from aiogram.types import Message

router = Router(name="reminder_settings")


@router.message(F.text.startswith("/reminder"))
async def set_reminder(message: Message) -> None:
    await message.answer(
        "⏰ ساعت یادآوری برای هر ختم جداست و خاموش نمی‌شود.\n\n"
        "از «⚙️ تنظیمات حساب» وارد «⏰ یادآوری» شو، ختم را انتخاب کن و ساعتش را تغییر بده."
    )
