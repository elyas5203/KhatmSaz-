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
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import KhatmStatus
import uuid

router = Router(name="creator_broadcast")

class CreatorBroadcastFlow(StatesGroup):
    choosing_target = State()
    entering_message = State()
    confirming = State()


@router.message(F.text == "📢 ارسال پیام گروهی")
@router.callback_query(F.data == "creator:broadcast")
async def start_broadcast(event: Message | CallbackQuery, state: FSMContext) -> None:
    """Owner request (2026-09-27): before composing, let the creator pick
    WHICH khatm's members to message — each of their active khatms, or «به همه
    ختم‌ها» (all their members, de-duplicated)."""
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
        khatms = [k for k in await khatm_service.list_created_by(session, user.id) if k.status == KhatmStatus.ACTIVE]

    await state.update_data(creator_id=str(user.id), platform=platform.value)

    if not khatms:
        await message.answer("هنوز ختم فعالی ندارید که بتوانید برای اعضایش پیام بفرستید.")
        if callback:
            await safe_answer_callback(callback)
        return

    rows = [[InlineKeyboardButton(text="📢 به همهٔ ختم‌ها", callback_data="cbroadcast_target:all")]]
    for k in khatms:
        rows.append([InlineKeyboardButton(text=f"🔹 {k.title}", callback_data=f"cbroadcast_target:{k.id}")])
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    prompt = "پیام گروهی برای اعضای کدام ختم ارسال شود؟"

    await state.set_state(CreatorBroadcastFlow.choosing_target)
    if callback:
        try:
            await callback.message.edit_text(prompt, reply_markup=markup)
        except Exception:
            await callback.message.answer(prompt, reply_markup=markup)
        await safe_answer_callback(callback)
    else:
        await message.answer(prompt, reply_markup=markup)


@router.callback_query(CreatorBroadcastFlow.choosing_target, F.data.startswith("cbroadcast_target:"))
async def choose_broadcast_target(callback: CallbackQuery, state: FSMContext) -> None:
    raw = callback.data.split(":", 1)[1]
    target_khatm_id = None if raw == "all" else raw
    data = await state.get_data()
    creator_id = uuid.UUID(data["creator_id"])

    async with session_scope() as session:
        khatm_uuid = uuid.UUID(target_khatm_id) if target_khatm_id else None
        audience_count = await broadcast_service.get_creator_audience_count(session, creator_id, khatm_id=khatm_uuid)
        broadcasts_last_7_days = await broadcast_service.get_broadcast_count_last_7_days(session, creator_id)
        cost = await broadcast_service.calculate_broadcast_cost(audience_count, broadcasts_last_7_days)

    await state.update_data(target_khatm_id=target_khatm_id, audience_count=audience_count, cost=cost)

    scope = "همهٔ ختم‌های شما" if target_khatm_id is None else "این ختم"
    info = (
        f"📢 ارسال پیام گروهی — {scope}\n\n"
        f"👥 تعداد مخاطبین فعال: {audience_count} نفر\n"
        f"📨 پیام‌های ۷ روز گذشته: {broadcasts_last_7_days}\n\n"
    )
    info += ("✅ هزینه این پیام: رایگان (۳ پیام اول در هفته)\n\n" if cost == 0
             else f"💳 هزینه این پیام: {cost:,} تومان\n\n")
    info += "لطفاً متن، عکس، فیلم یا فایل خود را ارسال کنید (برای لغو /cancel بزنید):"

    await state.set_state(CreatorBroadcastFlow.entering_message)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(info)
    await safe_answer_callback(callback)

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
        
        _target_raw = data.get("target_khatm_id")
        targets = await broadcast_service.get_broadcast_audience(
            session, creator_id, platform,
            khatm_id=uuid.UUID(_target_raw) if _target_raw else None,
        )
        
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
