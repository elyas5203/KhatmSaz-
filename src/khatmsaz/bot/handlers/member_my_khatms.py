from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select

from khatmsaz.core.db import session_scope
from khatmsaz.i18n import t
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.khatm.models import Khatm
from khatmsaz.bot.keyboards import MY_KHATMS_BUTTON_TEXTS

router = Router(name="member_my_khatms")

@router.message(F.text.in_(MY_KHATMS_BUTTON_TEXTS))
async def list_member_khatms(message: Message) -> None:
    bot = message.bot
    platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
    lang = getattr(bot, "khatmsaz_language", "fa")
    instance_id = getattr(bot, "khatmsaz_instance_id", None)
    
    async with session_scope() as session:
        user = await identity_service.resolve_or_provision_user(session, platform, message.chat.id)
        
        # Get participations filtered by instance_id
        # We need to implement a query since participation_service doesn't have it directly.
        from khatmsaz.modules.participation.models import Participation
        stmt = (
            select(Participation)
            .join(Khatm)
            .where(Participation.user_id == user.id)
            .where(Participation.joined_via_bot_instance_id == instance_id)
        )
        result = await session.execute(stmt)
        participations = result.scalars().all()
        
        if not participations:
            await message.answer(t("my_khatms.empty", lang))
            return
            
        for p in participations:
            khatm = await session.get(Khatm, p.khatm_id)
            buttons = []
            
            # Contribute button
            buttons.append([InlineKeyboardButton(
                text=t("my_khatms.button.contribute", lang),
                callback_data=f"portions:{khatm.id}"
            )])
            
            # Pause / Resume
            if p.is_paused:
                buttons.append([InlineKeyboardButton(
                    text=t("my_khatms.button.resume", lang),
                    callback_data=f"resume_participation:{khatm.id}"
                )])
            else:
                buttons.append([InlineKeyboardButton(
                    text=t("my_khatms.button.pause", lang),
                    callback_data=f"pause_participation:{khatm.id}"
                )])
                
            # Leave
            buttons.append([InlineKeyboardButton(
                text=t("my_khatms.button.leave", lang),
                callback_data=f"leave:{khatm.id}"
            )])
            
            kb = InlineKeyboardMarkup(inline_keyboard=buttons)
            
            progress = await participation_service.get_participation_progress_text(session, p.id, lang)
            text = f"🔹 {khatm.title}\n\n{progress}"
            await message.answer(text, reply_markup=kb)
