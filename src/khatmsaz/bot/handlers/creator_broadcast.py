from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timezone, timedelta

from khatmsaz.bot.keyboards import (
    bail_if_menu_button,
    safe_answer_callback,
    safe_clear_inline_keyboard,
    main_menu_keyboard,
    wallet_recharge_packages_keyboard,
)
from khatmsaz.bot.admin_notifications import notify_super_admins, notify_super_admins_photo
from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole
from khatmsaz.modules.broadcast import service as broadcast_service
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import KhatmStatus
from khatmsaz.modules.wallet import service as wallet_service
import math
import uuid

router = Router(name="creator_broadcast")

class CreatorBroadcastFlow(StatesGroup):
    choosing_target = State()
    entering_message = State()
    confirming = State()


async def _notify_admins_of_broadcast_request(
    *, item, creator_name: str, scope_title: str, source_bot=None,
) -> None:
    """Push the moderation queue item to admins with actionable buttons and media preview."""
    preview = (item.body or "").strip() or f"[{item.media_type or 'رسانه'} بدون متن]"
    if len(preview) > 500:
        preview = preview[:497] + "…"
    cost = getattr(item, "cost_toman", 0) or 0
    text = (
        "🔔 درخواست تازهٔ پیام گروهی\n\n"
        f"سازنده: {creator_name}\n"
        f"بخش: {scope_title}\n"
        f"مخاطب: {item.audience_count} نفر\n"
        f"مبلغ پرداختی: {cost:,} تومان\n"
        f"نوع رسانه: {getattr(item, 'media_type', None) or 'بدون رسانه'}\n\n"
        f"متن پیام:\n{preview}\n\n"
        f"کد درخواست: <code>{item.id}</code>\n\n"
        "می‌توانید با دکمه‌های زیر فوراً تأیید یا رد کنید یا در پنل ادمین بخش پیام‌های گروهی این کد را جست‌وجو نمایید:"
    )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ تأیید و ارسال",
                    callback_data=f"admin_broadcast:approve:{item.id}",
                ),
                InlineKeyboardButton(
                    text="❌ رد و عودت وجه",
                    callback_data=f"admin_broadcast:reject:{item.id}",
                ),
            ]
        ]
    )
    if item.media_type == "photo" and item.media_file_id_telegram:
        await notify_super_admins_photo(
            caption=text,
            photo_file_id=item.media_file_id_telegram,
            source_bot=source_bot,
            reply_markup=markup,
        )
    else:
        try:
            await notify_super_admins(text, reply_markup=markup)
        except TypeError:
            await notify_super_admins(text)


@router.callback_query(F.data.startswith("cbroadcast_khatm:"))
async def start_broadcast_for_khatm(callback: CallbackQuery, state: FSMContext) -> None:
    """MASTER-38: Direct entry to broadcast for a specific khatm from its management menu."""
    raw = callback.data.split(":", 1)[1]
    try:
        khatm_uuid = uuid.UUID(raw)
    except (ValueError, TypeError):
        await safe_answer_callback(callback, "شناسه ختم نامعتبر است.", show_alert=True)
        return

    bot = callback.bot
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, callback.message.chat.id)
        khatm = await khatm_service.get_khatm(session, khatm_uuid)
        if not khatm or khatm.creator_user_id != user.id or khatm.status != KhatmStatus.ACTIVE:
            await safe_answer_callback(callback, "این ختم فعال نیست یا شما سازندهٔ آن نیستید.", show_alert=True)
            return
        audience_count = len(await broadcast_service.audience_user_ids(session, user.id, khatm_id=khatm_uuid))
        policy = await broadcast_service.channel_policy(session, platform.value)
        unit_price = policy[1] if len(policy) > 1 and policy[1] > 0 else 150_000
        package_size = policy[2] if len(policy) > 2 and policy[2] > 0 else await broadcast_service.channel_package_size(session, platform.value)
        packages_count = max(1, math.ceil(audience_count / package_size)) if audience_count > 0 else 0
        total_cost = packages_count * unit_price
        balance, credit = await wallet_service.get_balances(session, user.id)
        wallet_balance = balance + credit

    await state.update_data(
        creator_id=str(user.id),
        platform=platform.value,
        target_khatm_id=str(khatm_uuid),
        target_title=khatm.title,
        audience_count=audience_count,
        unit_price=unit_price,
        package_size=package_size,
        packages_count=packages_count,
        total_cost=total_cost,
    )

    if audience_count == 0:
        text = (
            f"📢 ارسال پیام گروهی — «{khatm.title}»\n\n"
            "👥 تعداد مخاطبین فعال: ۰ نفر\n\n"
            "هنوز عضوی در این ختم ثبت‌نام نکرده است، بنابراین امکان ارسال پیام گروهی وجود ندارد."
        )
        back_kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت به مدیریت ختم", callback_data=f"my_khatms:manage:{khatm_uuid}")]]
        )
        await safe_clear_inline_keyboard(callback.message)
        await callback.message.answer(text, reply_markup=back_kb)
        await safe_answer_callback(callback)
        return

    if wallet_balance < total_cost:
        text = (
            f"📢 ارسال پیام گروهی — «{khatm.title}»\n\n"
            f"👥 تعداد مخاطبین فعال: {audience_count:,} نفر\n"
            f"💳 تعرفه هر بسته {package_size:,} نفری: {unit_price:,} تومان\n"
            f"📦 بسته‌های مورد نیاز: {packages_count} بسته (مجموعاً {total_cost:,} تومان)\n"
            f"💰 موجودی کیف پول شما: {wallet_balance:,} تومان\n\n"
            "⚠️ موجودی کیف پول شما برای ارسال این پیام گروهی کافی نیست.\n"
            "لازم است ابتدا کیف پول خود را شارژ فرمایید. لطفاً یکی از بسته‌های زیر را انتخاب کنید:"
        )
        kb = wallet_recharge_packages_keyboard(
            "fa",
            back_callback=f"my_khatms:manage:{khatm_uuid}",
            recheck_callback=f"cbroadcast_recheck:{khatm_uuid}",
        )
        await safe_clear_inline_keyboard(callback.message)
        await callback.message.answer(text, reply_markup=kb)
        await safe_answer_callback(callback)
        return

    text = (
        f"📢 ارسال پیام گروهی — «{khatm.title}»\n\n"
        f"👥 تعداد مخاطبین فعال: {audience_count:,} نفر\n"
        f"💳 تعرفه هر بسته {package_size:,} نفری: {unit_price:,} تومان\n"
        f"📦 بسته‌های مورد نیاز: {packages_count} بسته (مجموعاً {total_cost:,} تومان)\n"
        f"💰 موجودی کیف پول شما: {wallet_balance:,} تومان\n\n"
        "لطفاً متن، عکس، فیلم یا فایل خود را ارسال کنید (برای لغو دکمه زیر یا /cancel بزنید):"
    )
    cancel_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ انصراف", callback_data="cbroadcast:cancel")]]
    )
    await state.set_state(CreatorBroadcastFlow.entering_message)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(text, reply_markup=cancel_kb)
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cbroadcast_recheck:"))
async def recheck_broadcast_wallet(callback: CallbackQuery, state: FSMContext) -> None:
    """Re-check wallet balance when user clicked top-up."""
    data = await state.get_data()
    creator_id_raw = data.get("creator_id")
    if not creator_id_raw:
        await safe_answer_callback(callback, "نشست منقضی شده است. لطفاً مجدداً اقدام فرمایید.", show_alert=True)
        return
    creator_id = uuid.UUID(creator_id_raw)
    total_cost = data.get("total_cost", 0)
    target_title = data.get("target_title") or "این ختم"

    async with session_scope() as session:
        balance, credit = await wallet_service.get_balances(session, creator_id)
        effective_balance = balance + credit

    if effective_balance < total_cost:
        await safe_answer_callback(
            callback,
            f"موجودی شما هنوز کافی نیست ({effective_balance:,} تومان از {total_cost:,} تومان).",
            show_alert=True,
        )
        return

    text = (
        f"📢 ارسال پیام گروهی — «{target_title}»\n\n"
        f"✅ موجودی کیف پول شما با موفقیت تأیید شد ({effective_balance:,} تومان).\n\n"
        "لطفاً متن، عکس، فیلم یا فایل خود را ارسال کنید (برای لغو دکمه زیر یا /cancel بزنید):"
    )
    cancel_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ انصراف", callback_data="cbroadcast:cancel")]]
    )
    await state.set_state(CreatorBroadcastFlow.entering_message)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(text, reply_markup=cancel_kb)
    await safe_answer_callback(callback)


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
    rows.append([InlineKeyboardButton(text="❌ انصراف", callback_data="cbroadcast:cancel")])
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
    platform = data.get("platform", "TELEGRAM")

    async with session_scope() as session:
        khatm_uuid = uuid.UUID(target_khatm_id) if target_khatm_id else None
        target_khatm = await khatm_service.get_khatm(session, khatm_uuid) if khatm_uuid else None
        target_title = target_khatm.title if target_khatm else "همهٔ ختم‌های شما"
        audience_count = len(await broadcast_service.audience_user_ids(session, creator_id, khatm_id=khatm_uuid))
        policy = await broadcast_service.channel_policy(session, platform)
        unit_price = policy[1] if len(policy) > 1 and policy[1] > 0 else 150_000
        package_size = policy[2] if len(policy) > 2 and policy[2] > 0 else await broadcast_service.channel_package_size(session, platform)
        packages_count = max(1, math.ceil(audience_count / package_size)) if audience_count > 0 else 0
        total_cost = packages_count * unit_price
        balance, credit = await wallet_service.get_balances(session, creator_id)
        wallet_balance = balance + credit

    await state.update_data(
        target_khatm_id=target_khatm_id,
        target_title=target_title,
        audience_count=audience_count,
        unit_price=unit_price,
        package_size=package_size,
        packages_count=packages_count,
        total_cost=total_cost,
    )

    scope = f"«{target_title}»" if target_khatm else "همهٔ ختم‌های شما"

    if audience_count == 0:
        info = (
            f"📢 ارسال پیام گروهی — {scope}\n\n"
            "👥 تعداد مخاطبین فعال: ۰ نفر\n\n"
            "هنوز مخاطب فعالی در این بخش عضو نشده است، بنابراین امکان ارسال پیام گروهی وجود ندارد."
        )
        cancel_kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="❌ انصراف", callback_data="cbroadcast:cancel")]]
        )
        await safe_clear_inline_keyboard(callback.message)
        await callback.message.answer(info, reply_markup=cancel_kb)
        await safe_answer_callback(callback)
        return

    if wallet_balance < total_cost:
        info = (
            f"📢 ارسال پیام گروهی — {scope}\n\n"
            f"👥 تعداد مخاطبین فعال: {audience_count:,} نفر\n"
            f"💳 تعرفه هر بسته {package_size:,} نفری: {unit_price:,} تومان\n"
            f"📦 بسته‌های مورد نیاز: {packages_count} بسته (مجموعاً {total_cost:,} تومان)\n"
            f"💰 موجودی کیف پول شما: {wallet_balance:,} تومان\n\n"
            "⚠️ موجودی کیف پول شما برای ارسال این پیام گروهی کافی نیست.\n"
            "لازم است ابتدا کیف پول خود را شارژ فرمایید. لطفاً یکی از بسته‌های زیر را انتخاب کنید:"
        )
        recheck_target = target_khatm_id or "all"
        kb = wallet_recharge_packages_keyboard(
            "fa",
            back_callback="cbroadcast:cancel",
            recheck_callback=f"cbroadcast_recheck:{recheck_target}",
        )
        await safe_clear_inline_keyboard(callback.message)
        await callback.message.answer(info, reply_markup=kb)
        await safe_answer_callback(callback)
        return

    info = (
        f"📢 ارسال پیام گروهی — {scope}\n\n"
        f"👥 تعداد مخاطبین فعال: {audience_count:,} نفر\n"
        f"💳 تعرفه هر بسته {package_size:,} نفری: {unit_price:,} تومان\n"
        f"📦 بسته‌های مورد نیاز: {packages_count} بسته (مجموعاً {total_cost:,} تومان)\n"
        f"💰 موجودی کیف پول شما: {wallet_balance:,} تومان\n\n"
        "لطفاً متن، عکس، فیلم یا فایل خود را ارسال کنید (برای لغو دکمه زیر یا /cancel بزنید):"
    )

    cancel_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ انصراف", callback_data="cbroadcast:cancel")]]
    )
    await state.set_state(CreatorBroadcastFlow.entering_message)
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer(info, reply_markup=cancel_kb)
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
    elif message.voice:
        media_file_id = message.voice.file_id
        text = message.caption
        media_type = "voice"
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
        media_type=media_type,
    )

    data = await state.get_data()
    audience_count = data.get("audience_count", 0)
    total_cost = data.get("total_cost", 0)
    creator_id = uuid.UUID(data["creator_id"])
    async with session_scope() as session:
        balance, credit = await wallet_service.get_balances(session, creator_id)
        wallet_balance = balance + credit

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ تأیید و ثبت درخواست", callback_data="cbroadcast:confirm")],
            [InlineKeyboardButton(text="❌ انصراف", callback_data="cbroadcast:cancel")],
        ]
    )

    packages_count = data.get("packages_count", 1)
    package_size = data.get("package_size", 1000)
    confirm_text = (
        "آیا از ثبت این پیام گروهی اطمینان دارید؟\n\n"
        f"👥 تعداد مخاطب: {audience_count:,} نفر\n"
        f"📦 بسته‌های مورد نیاز: {packages_count} بسته {package_size:,} نفری\n"
        f"💰 هزینه ارسال: {total_cost:,} تومان\n"
        f"💳 موجودی فعلی کیف پول: {wallet_balance:,} تومان\n\n"
        f"پس از تأیید، مبلغ {total_cost:,} تومان از کیف پول شما کسر شده و پیام جهت بازبینی به مدیر سیستم ارسال می‌شود."
    )
    await message.answer(confirm_text, reply_markup=markup)
    await state.set_state(CreatorBroadcastFlow.confirming)


@router.callback_query(CreatorBroadcastFlow.confirming, F.data == "cbroadcast:confirm")
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    creator_id = uuid.UUID(data["creator_id"])
    audience_count = data.get("audience_count", 0)
    total_cost = data.get("total_cost", 0)
    platform = data["platform"]
    text = data.get("text")
    media_file_id = data.get("media_file_id")
    media_type = data["media_type"]

    await safe_clear_inline_keyboard(callback.message)
    _has_media = bool(media_type and media_type != "text" and media_file_id)
    if not (text or "").strip() and not _has_media:
        await callback.message.answer("برای صف تأیید مدیر، پیام باید متن یا رسانه داشته باشد.")
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
                body=text or "",
                media_type=media_type,
                media_file_id=media_file_id,
                cost_override=total_cost,
            )
            creator = await identity_service.find_by_id(session, creator_id)
            target_khatm = (
                await khatm_service.get_khatm(session, uuid.UUID(_target_raw))
                if _target_raw else None
            )
            creator_name = creator.display_name if creator and creator.display_name else "نامشخص"
            scope_title = target_khatm.title if target_khatm else "همهٔ ختم‌های سازنده"
    except broadcast_service.wallet_service.InsufficientFundsError:
        recheck_target = _target_raw or "all"
        kb = wallet_recharge_packages_keyboard(
            "fa",
            back_callback="cbroadcast:cancel",
            recheck_callback=f"cbroadcast_recheck:{recheck_target}",
        )
        await callback.message.answer(
            "💳 موجودی کیف پول شما برای ارسال این پیام گروهی کافی نیست. لطفاً ابتدا کیف پول خود را شارژ فرمایید:",
            reply_markup=kb,
        )
        await safe_answer_callback(callback)
        return
    except ValueError as exc:
        await callback.message.answer(f"پیام معتبر نیست یا مخاطبی برای آن پیدا نشد ({exc}).")
        await state.clear()
        await safe_answer_callback(callback)
        return
    await _notify_admins_of_broadcast_request(
        item=item, creator_name=creator_name, scope_title=scope_title, source_bot=callback.bot,
    )
    await state.clear()
    cost_text = f"{item.cost_toman:,} تومان"
    await callback.message.answer(
        f"✅ پیام شما با موفقیت برای تأیید محتوا ثبت شد.\n\n"
        f"👥 مخاطبان: {item.audience_count:,} نفر\n"
        f"💳 مبلغ کسر شده از کیف پول: {cost_text}\n\n"
        "پس از بررسی و تأیید توسط مدیریت، پیام برای تمام اعضا ارسال خواهد شد.",
        reply_markup=main_menu_keyboard("fa"),
    )
    await safe_answer_callback(callback)


@router.callback_query(F.data == "cbroadcast:cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await safe_clear_inline_keyboard(callback.message)
    await callback.message.answer("ارسال پیام گروهی لغو شد.", reply_markup=main_menu_keyboard("fa"))
    await safe_answer_callback(callback)


# -----------------------------------------------------------------------------
# MASTER-60: Live Seen / Engagement Analytics & In-Place Reporting Card
# -----------------------------------------------------------------------------

def _format_broadcast_stats_card(stats: dict) -> str:
    media_type = stats.get("media_type") or "text"
    media_names = {
        "text": "متن ساده",
        "photo": "تصویر / عکس",
        "voice": "پیام صوتی (ویس)",
        "audio": "فایل صوتی",
        "video": "ویدیو / فیلم",
        "document": "فایل / سند",
    }
    media_title = media_names.get(media_type, media_type)
    total = stats.get("total", 0)
    delivered = stats.get("delivered", total)
    seen = stats.get("seen", 0)
    unseen = stats.get("unseen", max(0, total - seen))
    seen_pct = stats.get("seen_percentage", 0.0)
    delivered_pct = 100 if total > 0 else 0

    media_note = ""
    if media_type in {"voice", "audio"}:
        media_note = f"\n🎧 وضعیت شنیدن صوت: {seen:,} نفر فایل صوتی را دریافت و گوش داده‌اند.\n"
    elif media_type in {"photo", "video", "document"}:
        media_note = f"\n🖼 وضعیت رسانه: {seen:,} نفر رسانه را دریافت و مشاهده نموده‌اند.\n"

    try:
        now_str = datetime.now(timezone(timedelta(hours=3, minutes=30))).strftime("%H:%M")
    except Exception:
        now_str = "هم‌اکنون"

    sent_time_str = "به‌تازگی"
    sent_at = stats.get("sent_at")
    if sent_at and hasattr(sent_at, "strftime"):
        try:
            sent_time_str = sent_at.astimezone(timezone(timedelta(hours=3, minutes=30))).strftime("%Y/%m/%d — %H:%M")
        except Exception:
            sent_time_str = str(sent_at)[:16]

    card = (
        "📊 گزارش لحظه‌ای بازخورد و سین پیام\n\n"
        f"🕋 ختم: «{stats.get('khatm_title', 'این ختم')}»\n"
        f"📝 نوع پیام: {media_title}\n"
        f"📅 زمان ارسال: {sent_time_str}\n\n"
        f"👥 کل مخاطبان: {total:,} نفر\n"
        f"📥 تحویل داده شده: {delivered:,} نفر ({delivered_pct}٪)\n"
        f"👁 مشاهده شده (سین خورده): {seen:,} نفر ({seen_pct}٪)\n"
        f"⏳ در انتظار مشاهده: {unseen:,} نفر ({round(max(0, 100 - seen_pct), 1)}٪)\n"
        f"{media_note}\n"
        f"🔄 آخرین به‌روزرسانی: {now_str}"
    )
    return card


def _build_stats_keyboard(broadcast_id: uuid.UUID, khatm_id: uuid.UUID | None = None) -> InlineKeyboardMarkup:
    khatm_back = f"my_khatms:manage:{khatm_id}" if khatm_id else "creator:broadcast"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 بروزرسانی آمار", callback_data=f"cbroadcast:refresh:{broadcast_id}"),
                InlineKeyboardButton(text="👥 اسامی مخاطبان", callback_data=f"cbroadcast:recipients:{broadcast_id}:0"),
            ],
            [
                InlineKeyboardButton(text="🔙 بازگشت به مدیریت ختم", callback_data=khatm_back),
            ],
        ]
    )


@router.callback_query(F.data.startswith("cbroadcast:stats:"))
async def view_broadcast_stats(callback: CallbackQuery) -> None:
    raw_id = callback.data.split(":", 2)[2]
    try:
        bc_id = uuid.UUID(raw_id)
    except (ValueError, TypeError):
        await safe_answer_callback(callback, "شناسه پیام نامعتبر است.", show_alert=True)
        return

    async with session_scope() as session:
        stats = await broadcast_service.get_analytics(session, bc_id)

    if not stats:
        await safe_answer_callback(callback, "اطلاعات آماری این پیام یافت نشد.", show_alert=True)
        return

    card_text = _format_broadcast_stats_card(stats)
    kb = _build_stats_keyboard(bc_id, stats.get("khatm_id"))

    if callback.message:
        try:
            await callback.message.edit_text(card_text, reply_markup=kb)
        except Exception:
            await callback.message.answer(card_text, reply_markup=kb)
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cbroadcast:refresh:"))
async def refresh_broadcast_stats(callback: CallbackQuery) -> None:
    raw_id = callback.data.split(":", 2)[2]
    try:
        bc_id = uuid.UUID(raw_id)
    except (ValueError, TypeError):
        await safe_answer_callback(callback, "شناسه نامعتبر است.", show_alert=True)
        return

    async with session_scope() as session:
        stats = await broadcast_service.get_analytics(session, bc_id)

    if not stats:
        await safe_answer_callback(callback, "اطلاعات آماری یافت نشد.", show_alert=True)
        return

    card_text = _format_broadcast_stats_card(stats)
    kb = _build_stats_keyboard(bc_id, stats.get("khatm_id"))

    if callback.message:
        try:
            await callback.message.edit_text(card_text, reply_markup=kb)
        except Exception:
            pass
    await safe_answer_callback(callback, "آمار با موفقیت بروز شد 🔄")


@router.callback_query(F.data.startswith("cbroadcast:recipients:"))
async def view_broadcast_recipients(callback: CallbackQuery) -> None:
    parts = callback.data.split(":")
    raw_id = parts[2]
    page = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    try:
        bc_id = uuid.UUID(raw_id)
    except (ValueError, TypeError):
        await safe_answer_callback(callback, "شناسه نامعتبر است.", show_alert=True)
        return

    page_size = 10
    async with session_scope() as session:
        recipients, total = await broadcast_service.list_recipients_page(
            session, bc_id, page=page, page_size=page_size,
        )

    if not recipients:
        await safe_answer_callback(callback, "فهرست مخاطبان هنوز ثبت نشده است.", show_alert=True)
        return

    total_pages = max(1, math.ceil(total / page_size))
    lines = ["👥 وضعیت مشاهده پیام توسط مخاطبان:\n"]
    for idx, r in enumerate(recipients, start=page * page_size + 1):
        if r["seen"]:
            seen_time = r["seen_at"].strftime("%H:%M") if r.get("seen_at") and hasattr(r["seen_at"], "strftime") else "مشاهده شده"
            lines.append(f"✅ {r['name']} — دیده شد ({seen_time})")
        else:
            lines.append(f"⏳ {r['name']} — در انتظار مشاهده")

    lines.append(f"\n📄 صفحه {page + 1} از {total_pages} (مجموعاً {total} مخاطب)")
    text = "\n".join(lines)

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ قبلی", callback_data=f"cbroadcast:recipients:{bc_id}:{page - 1}"))
    if page + 1 < total_pages:
        nav_row.append(InlineKeyboardButton(text="بعدی ➡️", callback_data=f"cbroadcast:recipients:{bc_id}:{page + 1}"))

    kb_rows = []
    if nav_row:
        kb_rows.append(nav_row)
    kb_rows.append([InlineKeyboardButton(text="🔙 بازگشت به آمار پیام", callback_data=f"cbroadcast:stats:{bc_id}")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)

    if callback.message:
        try:
            await callback.message.edit_text(text, reply_markup=kb)
        except Exception:
            await callback.message.answer(text, reply_markup=kb)
    await safe_answer_callback(callback)


@router.callback_query(F.data.startswith("cbroadcast_history:"))
async def view_khatm_broadcast_history(callback: CallbackQuery) -> None:
    raw_id = callback.data.split(":", 1)[1]
    try:
        khatm_uuid = uuid.UUID(raw_id)
    except (ValueError, TypeError):
        await safe_answer_callback(callback, "شناسه ختم نامعتبر است.", show_alert=True)
        return

    bot = callback.bot
    platform: Platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)

    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(
            session, platform, callback.message.chat.id,
        )
        broadcasts = await broadcast_service.repository.list_recent_broadcasts_for_creator(
            session, user.id, limit=5,
        )

    khatm_bcs = [b for b in broadcasts if b.khatm_id == khatm_uuid] if broadcasts else []
    if not khatm_bcs:
        await safe_answer_callback(callback, "هنوز پیام گروهی ارسالی برای این ختم ثبت نشده است.", show_alert=True)
        return

    rows = []
    for b in khatm_bcs:
        date_str = b.sent_at.strftime("%m/%d %H:%M") if b.sent_at else "ارسال‌شده"
        rows.append([
            InlineKeyboardButton(
                text=f"📊 پیام {date_str} ({b.audience_count} مخاطب)",
                callback_data=f"cbroadcast:stats:{b.id}",
            )
        ])
    rows.append([InlineKeyboardButton(text="🔙 بازگشت به مدیریت ختم", callback_data=f"my_khatms:manage:{khatm_uuid}")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    text = "📋 سوابق پیام‌های گروهی ارسال‌شده برای این ختم:\nلطفاً پیام مورد نظر را جهت مشاهده آمار سین انتخاب نمایید:"
    if callback.message:
        await callback.message.edit_text(text, reply_markup=kb)
    await safe_answer_callback(callback)
