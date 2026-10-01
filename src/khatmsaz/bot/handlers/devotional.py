"""User-facing complete dua/ziyarat library delivery."""

from html import escape
from io import BytesIO

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup, Message

from khatmsaz.bot.keyboards import safe_answer_callback
from khatmsaz.core.db import session_scope
from khatmsaz.core.bot_registry import get_registry
from khatmsaz.i18n import t
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.settings import service as settings_service

router = Router(name="devotional")


def _reciter_picker_keyboard(slug: str, variants: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"🎙 {variant.reciter_label or variant.reciter_id or 'قاری'}",
            callback_data=f"devotional_reciter:{slug}:{variant.reciter_id}",
        )]
        for variant in variants
    ])


async def _send_portable_media(
    message: Message, *, kind: str, asset_ref: str, platform: Platform, filename: str,
) -> None:
    """Retry a creator-bot file_id by downloading and re-uploading it.

    Telegram file identifiers belong to the bot that received the upload.
    Devotional media is registered through the creator bot but normally
    delivered by a member bot, so a direct reuse can fail with
    ``wrong file identifier``.  The live registry gives us the owning
    creator bot without persisting tokens or media bytes in the database.
    """
    sender = getattr(message, {
        "IMAGE": "answer_photo",
        "PDF": "answer_document",
        "AUDIO": "answer_audio",
    }[kind])
    direct_error: TelegramBadRequest | None = None
    try:
        await sender(asset_ref)
        return
    except TelegramBadRequest as exc:
        if "wrong file identifier" not in str(exc).lower():
            raise
        direct_error = exc

    source_bot = get_registry().get_creator_bot(platform)
    if source_bot is None or source_bot is message.bot:
        raise direct_error
    buffer = BytesIO()
    await source_bot.download(asset_ref, destination=buffer)
    await sender(BufferedInputFile(buffer.getvalue(), filename=filename))


async def deliver_devotional_media(
    session, message: Message, *, slug: str, asset, platform: Platform, lang: str,
) -> bool:
    """Sends every registered piece of media for one devotional asset:
    PDF, image page(s) in order, then audio. Owner request (2026-09-22):
    a dua can have several image pages (pagination) and several reciters
    to choose between — this checks the new multi-media table first,
    falling back to the older single audio_ref/image_ref columns for
    content registered before that table existed. Shared by `/devotional`
    and the khatm-participation recitation flow (`portions.py`)."""
    has_reading_media = False
    image_pages = await content_service.list_devotional_image_pages(session, slug, platform.value)
    if image_pages:
        for page in image_pages:
            await _send_portable_media(
                message, kind="IMAGE", asset_ref=page.asset_ref, platform=platform,
                filename=f"{slug}-{page.page_number}.jpg",
            )
        has_reading_media = True
    elif asset.image_ref and asset.image_platform == platform.value:
        await _send_portable_media(
            message, kind="IMAGE", asset_ref=asset.image_ref, platform=platform,
            filename=f"{slug}.jpg",
        )
        has_reading_media = True

    # Owner priority: readable media first — images, then the full PDF.
    pdf = await content_service.get_devotional_pdf(session, slug, platform.value)
    if pdf is not None:
        await _send_portable_media(
            message, kind="PDF", asset_ref=pdf.asset_ref, platform=platform,
            filename=f"{slug}.pdf",
        )
        has_reading_media = True

    audio_variants = await content_service.list_devotional_audio_variants(session, slug, platform.value)
    if not audio_variants and asset.audio_ref and asset.audio_platform == platform.value:
        await _send_portable_media(
            message, kind="AUDIO", asset_ref=asset.audio_ref, platform=platform,
            filename=f"{slug}.mp3",
        )
        return has_reading_media
    if len(audio_variants) == 1:
        await _send_portable_media(
            message, kind="AUDIO", asset_ref=audio_variants[0].asset_ref,
            platform=platform, filename=f"{slug}.mp3",
        )
    elif len(audio_variants) > 1:
        await message.answer(t("devotional.choose_reciter", lang), reply_markup=_reciter_picker_keyboard(slug, audio_variants))
    elif asset.audio_ref:
        await message.answer(t("devotional.audio_not_available_for_platform", lang))
    return has_reading_media


@router.callback_query(F.data.startswith("devotional_reciter:"))
async def send_devotional_reciter_choice(callback) -> None:
    _, slug, reciter_id = callback.data.split(":", 2)
    platform: Platform = getattr(callback.message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        variants = await content_service.list_devotional_audio_variants(session, slug, platform.value)
        asset = await content_service.get_devotional_asset(session, slug)
    chosen = next((v for v in variants if v.reciter_id == reciter_id), None)
    if chosen is None or asset is None:
        await safe_answer_callback(callback, "این صوت دیگر در دسترس نیست.", show_alert=True)
        return
    await callback.message.answer_audio(
        chosen.asset_ref,
        caption=f"🎙 {chosen.reciter_label or chosen.reciter_id} — {escape(asset.title)}",
    )
    await safe_answer_callback(callback)


@router.message(Command("devotional"))
async def send_devotional(message: Message, command: CommandObject) -> None:
    platform: Platform = getattr(message.bot, "khatmsaz_platform", Platform.TELEGRAM)
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        settings = await settings_service.get_or_create(session, user.id)
        lang = settings.language
    slug = (command.args or "").strip()
    if not slug:
        await message.answer(t("devotional.usage", lang))
        return
    async with session_scope() as session:
        asset = await content_service.get_devotional_asset(session, slug)
        if asset is None:
            await message.answer(t("devotional.not_found", lang))
            return
        has_reading_media = await deliver_devotional_media(
            session, message, slug=slug, asset=asset, platform=platform, lang=lang,
        )
        if asset.text_body and not has_reading_media:
            # Long devotional texts (e.g. Ziyarat Ashura) exceed Telegram's
            # ~4096-char message limit; admin-registered content embeds "\x1e"
            # as an explicit, author-controlled chunk boundary (never mid-couplet)
            # so each message stays intact. The body is trusted HTML (bold
            # Arabic lines) set only by admins via a script/command, not user
            # input, so it is intentionally not html-escaped here.
            chunks = asset.text_body.split("\x1e")
            await message.answer(f"📖 <b>{escape(asset.title)}</b>\n\n{chunks[0]}")
            for chunk in chunks[1:]:
                await message.answer(chunk)
