"""Conversation for admins to upload Dua media directly via Telegram/Bale."""

import asyncio
from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.bot.filters import AdminFilter
from khatmsaz.core.db import session_scope
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.content.migrator import mirror_devotional_media_to_bale
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
    video_caption = None
    if message.reply_to_message and message.reply_to_message.caption:
        video_caption = message.reply_to_message.caption.strip()
    elif target_msg.caption and not (target_msg.caption or "").strip().startswith("/"):
        video_caption = target_msg.caption.strip()

    try:
        async with session_scope() as session:
            if link:
                import re
                m = re.search(r"t\.me/([^/]+)/(\d+)", link)
                if m:
                    ch, mid = m.groups()
                    ref = f"tg_forward:@{ch.lstrip('@')}:{mid}"
                    media = await content_service.add_devotional_video_page(
                        session, slug=slug, asset_ref=ref, asset_platform=platform_val.value,
                        page_number=page_number, caption=video_caption,
                    )
                    await message.answer(f"✅ ویدیوی بخش {media.page_number} برای <code>{slug}</code> از طریق لینک کانال ثبت شد.")
                    if platform_val == Platform.TELEGRAM:
                        asyncio.create_task(
                            mirror_devotional_media_to_bale(
                                slug=slug,
                                kind="VIDEO",
                                page_number=media.page_number,
                                asset_ref=media.asset_ref,
                                caption=video_caption,
                                notify_chat_id=message.chat.id,
                                bot=message.bot,
                            )
                        )
                    return

            file_id = None
            if target_msg.video:
                file_id = target_msg.video.file_id
            elif target_msg.animation:
                file_id = target_msg.animation.file_id
            elif target_msg.document and (target_msg.document.mime_type or "").startswith("video/"):
                file_id = target_msg.document.file_id

            if file_id:
                media = await content_service.add_devotional_video_page(
                    session, slug=slug, asset_ref=file_id, asset_platform=platform_val.value,
                    page_number=page_number, caption=video_caption,
                )
                await message.answer(f"✅ ویدیوی بخش {media.page_number} برای <code>{slug}</code> با موفقیت ذخیره شد.")
                if platform_val == Platform.TELEGRAM:
                    asyncio.create_task(
                        mirror_devotional_media_to_bale(
                            slug=slug,
                            kind="VIDEO",
                            page_number=media.page_number,
                            asset_ref=media.asset_ref,
                            caption=video_caption,
                            notify_chat_id=message.chat.id,
                            bot=message.bot,
                        )
                    )
                return

            text_body = (target_msg.caption or target_msg.text or "").strip()
            if text_body:
                import re
                m = re.search(r"t\.me/([^/]+)/(\d+)", text_body)
                if m:
                    ch, mid = m.groups()
                    ref = f"tg_forward:@{ch.lstrip('@')}:{mid}"
                    media = await content_service.add_devotional_video_page(
                        session, slug=slug, asset_ref=ref, asset_platform=platform_val.value,
                        page_number=page_number, caption=video_caption,
                    )
                    await message.answer(f"✅ ویدیوی بخش {media.page_number} برای <code>{slug}</code> با موفقیت ثبت شد.")
                    if platform_val == Platform.TELEGRAM:
                        asyncio.create_task(
                            mirror_devotional_media_to_bale(
                                slug=slug,
                                kind="VIDEO",
                                page_number=media.page_number,
                                asset_ref=media.asset_ref,
                                caption=video_caption,
                                notify_chat_id=message.chat.id,
                                bot=message.bot,
                            )
                        )
                    return

        await message.answer("⚠️ ویدیویی یافت نشد. لطفاً روی یک ویدیو ریپلای کنید یا لینک پست را قرار دهید.")
    except Exception as exc:
        await message.answer(f"⚠️ خطا در ثبت ویدیو: {str(exc)}", parse_mode=None)


@router.message(Command("set_pdf", "add_pdf", "set_file", "add_file"))
async def set_pdf_direct(message: Message, command: CommandObject) -> None:
    """Owner shortcut: reply to a document/PDF to directly register a part-specific PDF."""
    args = (command.args or "").strip().split()
    if not args:
        await message.answer(
            "📖 <b>راهنمای ثبت مستقیم فایل PDF:</b>\n\n"
            "روی یک فایل PDF ریپلای کنید و بفرستید:\n"
            "<code>/set_pdf khutbah-ghadir 1</code>"
        )
        return

    slug = args[0].strip().lower()
    page_number = None
    for arg in args[1:]:
        if arg.isdigit():
            page_number = int(arg)
            break

    target_msg = message.reply_to_message or message
    platform_val = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    pdf_caption = None
    if message.reply_to_message and message.reply_to_message.caption:
        pdf_caption = message.reply_to_message.caption.strip()
    elif target_msg.caption and not (target_msg.caption or "").strip().startswith("/"):
        pdf_caption = target_msg.caption.strip()

    file_id = None
    if target_msg.document:
        file_id = target_msg.document.file_id

    if not file_id:
        await message.answer("⚠️ فایل سندی (PDF) یافت نشد. لطفاً روی پیام حاوی فایل PDF ریپلای کنید.")
        return

    try:
        async with session_scope() as session:
            media = await content_service.add_devotional_pdf_page(
                session, slug=slug, asset_ref=file_id, asset_platform=platform_val.value,
                page_number=page_number, caption=pdf_caption,
            )
            await message.answer(f"✅ 📄 فایل PDF بخش {media.page_number} برای <code>{slug}</code> با موفقیت ثبت شد.")
            if platform_val == Platform.TELEGRAM:
                asyncio.create_task(
                    mirror_devotional_media_to_bale(
                        slug=slug,
                        kind="PDF",
                        page_number=media.page_number,
                        asset_ref=media.asset_ref,
                        caption=pdf_caption,
                        notify_chat_id=message.chat.id,
                        bot=message.bot,
                    )
                )
    except Exception as exc:
        await message.answer(f"⚠️ خطا در ثبت فایل PDF: {str(exc)}", parse_mode=None)


@router.message(Command("set_audio", "add_audio"))
async def set_audio_direct(message: Message, command: CommandObject) -> None:
    """Owner shortcut: reply to an audio or voice message to register a part-specific audio."""
    args = (command.args or "").strip().split()
    if not args:
        await message.answer(
            "📖 <b>راهنمای ثبت مستقیم صوت:</b>\n\n"
            "روی یک فایل صوتی ریپلای کنید و بفرستید:\n"
            "<code>/set_audio khutbah-ghadir 1</code>"
        )
        return

    slug = args[0].strip().lower()
    page_number = None
    for arg in args[1:]:
        if arg.isdigit():
            page_number = int(arg)
            break

    target_msg = message.reply_to_message or message
    platform_val = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    audio_caption = None
    if message.reply_to_message and message.reply_to_message.caption:
        audio_caption = message.reply_to_message.caption.strip()
    elif target_msg.caption and not (target_msg.caption or "").strip().startswith("/"):
        audio_caption = target_msg.caption.strip()

    file_id = None
    if target_msg.audio:
        file_id = target_msg.audio.file_id
    elif target_msg.voice:
        file_id = target_msg.voice.file_id

    if not file_id:
        await message.answer("⚠️ فایل صوتی یافت نشد. لطفاً روی پیام صوتی ریپلای کنید.")
        return

    try:
        async with session_scope() as session:
            media = await content_service.add_devotional_audio_page(
                session, slug=slug, asset_ref=file_id, asset_platform=platform_val.value,
                page_number=page_number, caption=audio_caption,
            )
            await message.answer(f"✅ 🔊 صوت بخش {media.page_number} برای <code>{slug}</code> با موفقیت ثبت شد.")
            if platform_val == Platform.TELEGRAM:
                asyncio.create_task(
                    mirror_devotional_media_to_bale(
                        slug=slug,
                        kind="AUDIO",
                        page_number=media.page_number,
                        asset_ref=media.asset_ref,
                        caption=audio_caption,
                        notify_chat_id=message.chat.id,
                        bot=message.bot,
                    )
                )
    except Exception as exc:
        await message.answer(f"⚠️ خطا در ثبت صوت: {str(exc)}", parse_mode=None)


@router.message(Command("set_media", "add_media"))
async def set_media_direct(message: Message, command: CommandObject) -> None:
    """Universal shortcut: auto-detects video, PDF or audio and registers for the part."""
    target_msg = message.reply_to_message or message
    if target_msg.video or target_msg.animation or (target_msg.document and (target_msg.document.mime_type or "").startswith("video/")):
        await set_video_direct(message, command)
    elif target_msg.document and target_msg.document.mime_type == "application/pdf":
        await set_pdf_direct(message, command)
    elif target_msg.audio or target_msg.voice:
        await set_audio_direct(message, command)
    else:
        # Fallback to checking link or video
        await set_video_direct(message, command)


@router.message(Command("media", "list_media", "videos", "list_videos"))
async def list_media_command(message: Message, command: CommandObject) -> None:
    """Lists all registered media (Video, PDF, Audio) for a devotional slug."""
    slug = (command.args or "").strip().lower() or "khutbah-ghadir"
    platform_val = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        from khatmsaz.modules.content.models import DevotionalAsset, DevotionalMedia
        from sqlalchemy import select
        asset = await session.scalar(select(DevotionalAsset).where(DevotionalAsset.slug == slug))
        if asset is None:
            await message.answer(f"ℹ️ هیچ محتوایی با شناسه <code>{slug}</code> یافت نشد.")
            return
        all_media = (await session.execute(
            select(DevotionalMedia)
            .where(
                DevotionalMedia.devotional_asset_id == asset.id,
                DevotionalMedia.asset_platform == platform_val.value,
            )
            .order_by(DevotionalMedia.page_number.asc(), DevotionalMedia.kind.asc())
        )).scalars().all()

    if not all_media:
        await message.answer(f"ℹ️ هنوز هیچ رسانه‌ای برای <code>{slug}</code> ثبت نشده است.")
        return

    # Group by page_number
    grouped: dict[int, dict[str, str]] = {}
    for m in all_media:
        p = m.page_number or 1
        grouped.setdefault(p, {})[m.kind] = m.asset_ref[:25] + "..."

    lines = [f"📚 <b>رسانه‌های ثبت‌شده برای «{asset.title}» (<code>{slug}</code>):</b>\n"]
    for p in sorted(grouped.keys()):
        kinds = grouped[p]
        v_icon = "🎬 ویدیو ✅" if "VIDEO" in kinds else "🎬 ویدیو ❌"
        d_icon = "📄 فایل PDF ✅" if "PDF" in kinds else "📄 فایل PDF ❌"
        a_icon = "🔊 صوت ✅" if "AUDIO" in kinds else "🔊 صوت ❌"
        lines.append(f"• <b>بخش {p}:</b> {v_icon} | {d_icon} | {a_icon}")

    lines.append(f"\nمجموع: <b>{len(grouped)} بخش</b> در دیتابیس ثبت شده است.")
    await message.answer("\n".join(lines))


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
        if platform_val == Platform.TELEGRAM and getattr(result, "media", None):
            m = result.media
            asyncio.create_task(
                mirror_devotional_media_to_bale(
                    slug=slug,
                    kind=m.kind,
                    page_number=m.page_number,
                    asset_ref=m.asset_ref,
                    caption=m.reciter_label,
                    reciter_id=m.reciter_id,
                    reciter_label=m.reciter_label,
                    notify_chat_id=message.chat.id,
                    bot=message.bot,
                )
            )
    else:
        await message.answer("⚠️ نوع فایل پشتیبانی نشد.")


@router.callback_query(F.data == "manage_content:finish", ManageContentState.waiting_for_media)
async def finish_manage_content(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("✅ تمام فایل‌ها با موفقیت ذخیره و مرتبط شدند. خسته نباشید!")
    await callback.answer()
