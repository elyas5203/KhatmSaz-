"""Conversation for admins to upload Dua media directly via Telegram/Bale."""

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
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
async def start_manage_content(message: Message, state: FSMContext, command: CommandObject) -> None:
    slug = (command.args or "").strip().lower()
    if slug:
        await state.update_data(slug=slug)
        await state.set_state(ManageContentState.waiting_for_media)
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ پایان و ذخیره", callback_data="manage_content:finish")]
        ])
        await message.answer(
            f"کد اتصال تنظیم شد: <code>{slug}</code>\n\n"
            "حالا ویدیوها، صوت‌ها یا فایل‌ها را یکی پس از دیگری بفرستید یا فوروارد کنید.\n"
            "هر فایل فوراً ثبت می‌شود.\n\n"
            "هروقت تمام شد دکمه زیر را بزنید:",
            reply_markup=markup,
        )
        return

    await state.set_state(ManageContentState.waiting_for_slug)
    await message.answer(
        "✨ <b>مدیریت محتوای ادعیه، زیارات و خطبه‌ها</b>\n\n"
        "لطفاً کد اتصال (slug) محتوای مورد نظرتان را بفرستید (مثلاً <code>khutbah-fadakiah</code> یا <code>ziyarat-ashura</code>).\n"
        "اگر این کد وجود نداشته باشد، ثبت خواهد شد."
    )


@router.message(Command("set_video", "add_video"))
async def set_video_direct(message: Message, command: CommandObject) -> None:
    """Owner shortcut: reply to any video or send a channel link to directly register a video part."""
    args = (command.args or "").strip().split()
    if not args:
        await message.answer(
            "📖 <b>راهنمای ثبت مستقیم ویدیو:</b>\n\n"
            "۱. این دستور را روی یک پیام ویدیویی <b>ریپلای</b> کنید:\n"
            "<code>/set_video khutbah-fadakiah 1</code>\n\n"
            "۲. یا همراه با لینک پیام در کانال تلگرام ارسال کنید:\n"
            "<code>/set_video khutbah-fadakiah 1 https://t.me/khedmatgozaran_group/25286</code>"
        )
        return

    slug = args[0].strip().lower()
    page_number = None
    link = None

    for arg in args[1:]:
        if arg.isdigit():
            page_number = int(arg)
        elif "t.me/" in arg:
            link = arg

    target_msg = message.reply_to_message or message
    platform_val = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)

    async with session_scope() as session:
        if link:
            import re
            m = re.search(r"t\.me/([^/]+)/(\d+)", link)
            if m:
                ch, mid = m.groups()
                ref = f"tg_forward:@{ch.lstrip('@')}:{mid}"
                media = await content_service.add_devotional_video_page(
                    session, slug=slug, asset_ref=ref, asset_platform=platform_val.value,
                    page_number=page_number,
                )
                await message.answer(f"✅ ویدیوی بخش {media.page_number} برای <code>{slug}</code> از طریق لینک کانال ثبت شد.")
                return

        file_id = None
        if target_msg.video:
            file_id = target_msg.video.file_id
        elif target_msg.document and (target_msg.document.mime_type or "").startswith("video/"):
            file_id = target_msg.document.file_id

        if file_id:
            media = await content_service.add_devotional_video_page(
                session, slug=slug, asset_ref=file_id, asset_platform=platform_val.value,
                page_number=page_number,
            )
            await message.answer(f"✅ ویدیوی بخش {media.page_number} برای <code>{slug}</code> با موفقیت ذخیره شد.")
            return

        if target_msg.text:
            import re
            m = re.search(r"t\.me/([^/]+)/(\d+)", target_msg.text)
            if m:
                ch, mid = m.groups()
                ref = f"tg_forward:@{ch.lstrip('@')}:{mid}"
                media = await content_service.add_devotional_video_page(
                    session, slug=slug, asset_ref=ref, asset_platform=platform_val.value,
                    page_number=page_number,
                )
                await message.answer(f"✅ ویدیوی بخش {media.page_number} برای <code>{slug}</code> با موفقیت ثبت شد.")
                return

    await message.answer("⚠️ ویدیویی یافت نشد. لطفاً روی یک ویدیو ریپلای کنید یا لینک پست را قرار دهید.")


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
