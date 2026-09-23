"""Conversation for admins to upload Dua media directly via Telegram/Bale."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.bot.filters import AdminFilter
from khatmsaz.core.db import session_scope
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.identity.models import Platform


router = Router(name="manage_content")
router.message.filter(AdminFilter(permission="CONTENT_MANAGE"))
router.callback_query.filter(AdminFilter(permission="CONTENT_MANAGE"))


class ManageContentState(StatesGroup):
    waiting_for_slug = State()
    waiting_for_media = State()


@router.message(Command("manage_content"))
async def start_manage_content(message: Message, state: FSMContext) -> None:
    await state.set_state(ManageContentState.waiting_for_slug)
    await message.answer(
        "✨ <b>مدیریت محتوای ادعیه و زیارات</b>\n\n"
        "لطفاً کد اتصال (slug) دعا یا زیارت مورد نظرت رو بفرست (مثلاً `ahad` یا `ziyarat-ashura`).\n"
        "اگر این کد وجود نداشته باشه، یکی جدید ساخته می‌شه."
    )


@router.message(ManageContentState.waiting_for_slug)
async def receive_slug(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    slug = message.text.strip().lower()
    await state.update_data(slug=slug)
    await state.set_state(ManageContentState.waiting_for_media)
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ پایان و ذخیره", callback_data="manage_content:finish")]
    ])
    
    await message.answer(
        f"کد اتصال تنظیم شد: <code>{slug}</code>\n\n"
        "حالا هر متن طولانی، عکس، فایل PDF، یا صوتی که برای این دعا داری رو اینجا بفرست یا فوروارد کن.\n"
        "هر فایلی که بفرستی همون لحظه برای این پلتفرم تو دیتابیس ثبت می‌شه.\n\n"
        "هروقت تموم شد، دکمه زیر رو بزن:",
        reply_markup=markup
    )


@router.message(ManageContentState.waiting_for_media)
async def receive_media(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    slug = data.get("slug")
    if not slug:
        await state.clear()
        return

    platform_val = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    
    async with session_scope() as session:
        result = await content_service.append_devotional_media_from_message(
            session, slug, message, platform=platform_val
        )
    
    if result:
        await message.answer(f"✅ {result} ثبت شد.")
    else:
        await message.answer("⚠️ نوع فایل پشتیبانی نشد.")


@router.callback_query(F.data == "manage_content:finish", ManageContentState.waiting_for_media)
async def finish_manage_content(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("✅ تمام فایل‌ها با موفقیت ذخیره و مرتبط شدند. خسته نباشید!")
    await callback.answer()
