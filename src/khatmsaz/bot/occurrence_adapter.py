"""Member-only delivery with durable component receipts."""
from html import escape
from io import BytesIO
from types import SimpleNamespace

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup

from khatmsaz.core.bot_registry import get_registry
from khatmsaz.modules.identity import service as identities
from khatmsaz.modules.content import service as content
from khatmsaz.modules.settings import service as settings_service
from khatmsaz.modules.share_occurrence import repository, service
from khatmsaz.i18n import t


def keyboard(occurrence):
    from khatmsaz.bot.member_copy import done_button_label
    family = occurrence.content_spec.get("family", "salawat") if occurrence.content_spec else "salawat"
    lang = occurrence.content_spec.get("language", "fa") if occurrence.content_spec else "fa"
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text=done_button_label(family, lang), callback_data=f"share_done:{occurrence.id}",
    )]])


async def route(session, part, occurrence):
    from khatmsaz.modules.bot_registry import service as bots
    if part.joined_via_bot_instance_id != occurrence.bot_instance_id:
        return None, None
    record = await bots.get_instance(session, occurrence.bot_instance_id)
    if record is None or not record.is_active or record.bot_role != "MEMBER":
        return None, None
    bot = get_registry().get_by_instance_id(occurrence.bot_instance_id)
    if bot is None or getattr(bot, "khatmsaz_role", None) != "MEMBER":
        return None, None
    if record.platform != getattr(bot, "khatmsaz_platform", None):
        return None, None
    for identity in await identities.list_identities_for_user(session, part.user_id):
        if identity.platform == getattr(bot, "khatmsaz_platform", None):
            return bot, int(identity.subject)
    return None, None


def label(khatm, occurrence):
    from khatmsaz.bot.member_copy import share_label
    lang = occurrence.content_spec.get("language", "fa")
    if occurrence.unit == "PAGE":
        pages = "، ".join(f"{a} تا {b}" if a != b else str(a) for a, b in occurrence.content_spec["ranges"])
        return t("share.pages", lang, title=escape(khatm.title), pages=pages)
    amount = share_label(occurrence.content_spec.get("family", "salawat"), count=occurrence.amount, lang=lang)
    return t("share.amount", lang, title=escape(khatm.title), amount=amount)


async def send_control(session, part, khatm, occurrence, purpose, *, now):
    records = await repository.list_messages(session, occurrence.id)
    if any(r.component_key == purpose for r in records):
        return True
    bot, chat = await route(session, part, occurrence)
    if bot is None:
        return False
    text = label(khatm, occurrence)
    if purpose == "FOLLOWUP":
        text += "\n" + t("share.followup", occurrence.content_spec.get("language", "fa"))
    elif purpose == "DEADLINE":
        text += "\n" + t("share.deadline", occurrence.content_spec.get("language", "fa"))
    elif purpose == "RESERVATION_WARNING":
        text += "\n" + t("portions.open_reservation_warning", occurrence.content_spec.get("language", "fa"), count=occurrence.amount)
    msg = await bot.send_message(chat_id=chat, text=text, reply_markup=keyboard(occurrence))
    await service.record_message(session, occurrence_id=occurrence.id, bot_instance_id=occurrence.bot_instance_id,
        component_key=purpose, purpose="FOLLOWUP" if purpose == "RESERVATION_WARNING" else purpose, chat_id=str(chat), message_id=msg.message_id, sent_at=now)
    return True


async def deliver_occurrence(session, part, khatm, occurrence, *, now):
    bot, chat = await route(session, part, occurrence)
    if bot is None:
        return False
    records = {r.component_key: r for r in await repository.list_messages(session, occurrence.id)}
    components = occurrence.content_spec.get("delivery_components")
    collecting = components is None
    if collecting:
        from khatmsaz.bot.member_copy import content_family
        settings = await settings_service.get_or_create(session, part.user_id)
        occurrence.content_spec = {**occurrence.content_spec,
            "family": await content_family(session, khatm),
            "language": getattr(bot, "khatmsaz_language", None) or settings.language}
    components = components or []
    async def collect(method, **kwargs):
        markup = kwargs.get("reply_markup")
        if markup is not None:
            kwargs["reply_markup"] = markup.model_dump(mode="json", exclude_none=True)
        components.append({"method": method, "kwargs": kwargs})
        return SimpleNamespace(message_id=len(components))
    if collecting and occurrence.unit == "PAGE":
        seen = set()
        for start, end in occurrence.content_spec["ranges"]:
            delivery = await content.resolve_current_quran_delivery(session, khatm=khatm,
                user_id=part.user_id, page_start=start, page_end=end,
                asset_platform=bot.khatmsaz_platform.value, audio_enabled=part.quran_audio_enabled)
            if not any(delivery.get(kind) for kind in ("image", "audio", "text")):
                return False
            for kind in ("image", "audio", "text"):
                for asset in delivery.get(kind) or []:
                    key = (kind, asset.asset_ref)
                    if key in seen:
                        continue
                    seen.add(key)
                    forward = content.decode_telegram_forward_ref(asset.asset_ref)
                    if forward:
                        await collect("forward_message", from_chat_id=forward[0], message_id=forward[1])
                    else:
                        method, arg = {"image": ("send_photo", "photo"), "audio": ("send_audio", "audio"), "text": ("send_message", "text")}[kind]
                        await collect(method, **{arg: asset.asset_ref})
    elif collecting:
        from khatmsaz.bot.notify_adapter import send_devotional_content
        settings = await settings_service.get_or_create(session, part.user_id)
        if not await send_devotional_content(session, bot.khatmsaz_platform.value, str(chat),
                khatm=khatm, lang=occurrence.content_spec["language"], bot_instance_id=occurrence.bot_instance_id, receipt_sender=collect):
            return False
    if not components:
        return False
    if collecting:
        occurrence.content_spec = {**occurrence.content_spec, "delivery_components": components}
        await session.flush()
    for index, component in enumerate(components):
        key = f"content:{index}"
        if key in records:
            continue
        method, kwargs = component["method"], dict(component["kwargs"])
        if kwargs.get("reply_markup"):
            kwargs["reply_markup"] = InlineKeyboardMarkup.model_validate(kwargs["reply_markup"])
        try:
            message = await getattr(bot, method)(chat_id=chat, **kwargs)
        except TelegramBadRequest as exc:
            arg = {"send_photo": "photo", "send_audio": "audio", "send_document": "document"}.get(method)
            if arg is None or "wrong file identifier" not in str(exc).lower():
                raise
            owner = get_registry().get_creator_bot(bot.khatmsaz_platform)
            if owner is None or owner is bot:
                raise
            buffer = BytesIO()
            await owner.download(kwargs[arg], destination=buffer)
            kwargs[arg] = BufferedInputFile(buffer.getvalue(), filename=f"share.{ {'photo':'jpg','audio':'mp3','document':'pdf'}[arg] }")
            message = await getattr(bot, method)(chat_id=chat, **kwargs)
        await service.record_message(session, occurrence_id=occurrence.id,
            bot_instance_id=occurrence.bot_instance_id, component_key=key, purpose="CONTENT",
            chat_id=str(chat), message_id=message.message_id, sent_at=now)
    return await send_control(session, part, khatm, occurrence, "ACTION", now=now)


async def cleanup(session, part, occurrence):
    bot, _ = await route(session, part, occurrence)
    if bot is None:
        return
    for receipt in await service.cleanup_candidates(session, occurrence.id):
        try:
            await bot.delete_message(chat_id=int(receipt.chat_id), message_id=receipt.message_id)
        except Exception:
            continue
        await service.record_message_deleted(session, occurrence.id, receipt.id)
