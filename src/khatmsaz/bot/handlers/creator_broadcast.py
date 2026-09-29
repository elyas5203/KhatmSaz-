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
from khatmsaz.modules.broadcast import service as broadcast_service
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
        khatms = [k for k in await khatm_service.list_my_created(session, user.id) if k.status == KhatmStatus.ACTIVE]

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
        audience_count = len(await broadcast_service.audience_user_ids(session, creator_id, khatm_id=khatm_uuid))
        free_count, price = await broadcast_service.channel_policy(session, data["platform"])

    await state.update_data(target_khatm_id=target_khatm_id, audience_count=audience_count)

    scope = "همهٔ ختم‌های شما" if target_khatm_id is None else "این ختم"
    info = (
        f"📢 ارسال پیام گروهی — {scope}\n\n"
        f"👥 تعداد مخاطبین فعال: {audience_count} نفر\n"
        f"🎁 سهمیهٔ رایگان این کانال: {free_count} پیام در ۷ روز\n"
        f"💳 هزینهٔ هر پیام بعد از سهمیه: {price:,} تومان\n\n"
    )
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
    platform = data["platform"]
    text = data.get("text")
    media_file_id = data.get("media_file_id")
    media_type = data["media_type"]
    
    await safe_clear_inline_keyboard(callback.message)
    if not (text or "").strip():
        await callback.message.answer("برای صف تأیید مدیر، پیام باید متن داشته باشد.")
        await state.clear()
        await safe_answer_callback(callback)
        return
    _target_raw = data.get("target_khatm_id")
    try:
        async with session_scope() as session:
            item = await broadcast_service.submit(
                session,
                creator_user_id=creator_id,
                khatm_id=uuid.UUID(_target_raw) if _target_raw else None,
                channel=platform,
                body=text,
            )
    except ValueError:
        await callback.message.answer("پیام معتبر نیست یا مخاطبی برای آن پیدا نشد.")
        await state.clear()
        await safe_answer_callback(callback)
        return
    await state.clear()
    cost_text = "رایگان" if item.cost_toman == 0 else f"{item.cost_toman:,} تومان"
    await callback.message.answer(
        f"✅ پیام برای تأیید مدیر ثبت شد.\n👥 مخاطب: {item.audience_count} نفر\n💳 هزینه پس از تأیید: {cost_text}",
        reply_markup=main_menu_keyboard("fa"),
    )
    await safe_answer_callback(callback)

@router.callback_query(CreatorBroadcastFlow.confirming, F.data == "cbroadcast:cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer("ارسال پیام گروهی لغو شد.", reply_markup=main_menu_keyboard("fa"))
    await safe_answer_callback(callback)
