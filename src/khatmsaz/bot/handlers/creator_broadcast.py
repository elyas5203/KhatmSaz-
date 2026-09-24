from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from khatmsaz.bot.keyboards import bail_if_menu_button, safe_answer_callback, safe_clear_inline_keyboard, main_menu_keyboard
from khatmsaz.bot.notify_adapter import get_notify_fn
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.creator_broadcast import service as broadcast_service
import uuid

router = Router(name="creator_broadcast")

class CreatorBroadcastFlow(StatesGroup):
    entering_message = State()
    confirming = State()


@router.message(F.text == "📢 ارسال پیام گروهی")
@router.callback_query(F.data == "creator:broadcast")
async def start_broadcast(event: Message | CallbackQuery, state: FSMContext) -> None:
    bot = event.bot
    message = event if isinstance(event, Message) else event.message
    callback = event if isinstance(event, CallbackQuery) else None
    
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        if user.role not in (UserRole.CREATOR, UserRole.SUPER_ADMIN):
            await message.answer("شما دسترسی سازنده ندارید.")
            if callback:
                await safe_answer_callback(callback)
            return
            
        audience_count = await broadcast_service.get_creator_audience_count(session, user.id)
        broadcasts_last_7_days = await broadcast_service.get_broadcast_count_last_7_days(session, user.id)
        cost = await broadcast_service.calculate_broadcast_cost(audience_count, broadcasts_last_7_days)
        
        await state.update_data(
            creator_id=str(user.id),
            audience_count=audience_count,
            cost=cost,
            platform=platform.value
        )
        
        info = (
            f"📢 ارسال پیام گروهی\n\n"
            f"👥 تعداد مخاطبین فعال شما: {audience_count} نفر\n"
            f"📨 پیام‌های ارسال شده در ۷ روز گذشته: {broadcasts_last_7_days}\n\n"
        )
        if cost == 0:
            info += "✅ هزینه این پیام: **رایگان** (۳ پیام اول در هفته)\n\n"
        else:
            info += f"💳 هزینه این پیام: **{cost:,} تومان**\n\n"
            
        info += "لطفاً متن، عکس، فیلم یا فایل خود را ارسال کنید (برای لغو /cancel بزنید):"
        
        await state.set_state(CreatorBroadcastFlow.entering_message)
        if callback:
            await callback.message.edit_text(info)
            await safe_answer_callback(callback)
        else:
            await message.answer(info)

@router.message(CreatorBroadcastFlow.entering_message)
async def receive_broadcast_message(message: Message, state: FSMContext) -> None:
    if await bail_if_menu_button(message, state):
        return
        
    media_file_id = None
    media_type = None
    text = None
    
    if message.text:
        text = message.text
        media_type = "text"
    elif message.photo:
        media_file_id = message.photo[-1].file_id
        text = message.caption
        media_type = "photo"
    elif message.video:
        media_file_id = message.video.file_id
        text = message.caption
        media_type = "video"
    elif message.document:
        media_file_id = message.document.file_id
        text = message.caption
        media_type = "document"
    else:
        await message.answer("فرمت ارسال شده پشتیبانی نمی‌شود.")
        return
        
    await state.update_data(
        text=text,
        media_file_id=media_file_id,
        media_type=media_type
    )
    
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ تایید و ارسال", callback_data="cbroadcast:confirm")],
            [InlineKeyboardButton(text="❌ انصراف", callback_data="cbroadcast:cancel")],
        ]
    )
    
    await message.answer("آیا از ارسال این پیام برای تمام مخاطبین خود اطمینان دارید؟", reply_markup=markup)
    await state.set_state(CreatorBroadcastFlow.confirming)

@router.callback_query(CreatorBroadcastFlow.confirming, F.data == "cbroadcast:confirm")
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    creator_id = uuid.UUID(data["creator_id"])
    audience_count = data["audience_count"]
    cost = data["cost"]
    platform = data["platform"]
    text = data.get("text")
    media_file_id = data.get("media_file_id")
    media_type = data["media_type"]
    
    if cost > 0:
        await safe_clear_inline_keyboard(callback.message)
        await callback.message.answer(
            "⚠️ ارسال پیام گروهی پولی در حال حاضر غیرفعال است (در حال توسعه سیستم پرداخت). لطفاً بعداً تلاش کنید."
        )
        await state.clear()
        await safe_answer_callback(callback)
        return

    is_paid = True
    
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer("در حال ارسال پیام...")
    
    async with session_scope() as session:
        # Save broadcast
        broadcast = await broadcast_service.create_broadcast(
            session, creator_id, platform, text, media_file_id, media_type, cost, audience_count, is_paid
        )
        
        targets = await broadcast_service.get_broadcast_audience(session, creator_id, platform)
        
    # Send
    success = 0
    failed = 0
    bot = callback.bot
    for chat_id in targets:
        try:
            if media_type == "text":
                await bot.send_message(chat_id, text)
            elif media_type == "photo":
                await bot.send_photo(chat_id, media_file_id, caption=text)
            elif media_type == "video":
                await bot.send_video(chat_id, media_file_id, caption=text)
            elif media_type == "document":
                await bot.send_document(chat_id, media_file_id, caption=text)
            success += 1
        except Exception as e:
            failed += 1
            import logging
            logging.getLogger("khatmsaz.broadcast").error(f"Failed to send broadcast to {chat_id}: {e}")
            
    await state.clear()
    await callback.message.answer(f"✅ پیام شما با موفقیت برای {success} نفر ارسال شد.\n❌ تعداد ناموفق: {failed}", reply_markup=main_menu_keyboard("fa"))
    await safe_answer_callback(callback)

@router.callback_query(CreatorBroadcastFlow.confirming, F.data == "cbroadcast:cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer("ارسال پیام گروهی لغو شد.", reply_markup=main_menu_keyboard("fa"))
    await safe_answer_callback(callback)
