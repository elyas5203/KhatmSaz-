from typing import Any, Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from khatmsaz.config import get_settings
from khatmsaz.core.db import session_scope
from khatmsaz.modules.identity import service as identity_service
from khatmsaz.modules.identity.models import Platform, UserRole

class AdminFilter(BaseFilter):
    """
    Checks if the user has admin privileges.
    For now, we simply check if the user role is SUPER_ADMIN.
    """
    def __init__(self, permission: str = ""):
        self.permission = permission

    async def __call__(self, event: Union[Message, CallbackQuery], bot: Any) -> bool:
        platform = getattr(bot, "khatmsaz_platform", Platform.TELEGRAM)
        
        chat_id = None
        if hasattr(event, "chat") and event.chat:
            chat_id = getattr(event.chat, "id", None)
        elif hasattr(event, "message") and event.message and hasattr(event.message, "chat"):
            chat_id = getattr(event.message.chat, "id", None)
            
        if not chat_id:
            return False

        settings = get_settings()
        str_chat_id = str(chat_id)

        # 1. Direct configuration check (DEC-PY-0013 / WP-03)
        admin_id_str = (
            settings.super_admin_bale_chat_ids
            if platform == Platform.BALE
            else settings.super_admin_telegram_chat_ids
        )
        admin_ids = {x.strip() for x in admin_id_str.split(",") if x.strip()}
        if str_chat_id in admin_ids:
            return True

        # 2. Database user role check
        async with session_scope() as session:
            user = await identity_service.find_by_platform(session, platform, str_chat_id)
            if user is None:
                return False
                
            if user.role == UserRole.SUPER_ADMIN:
                return True
                
            # TODO: If we want to check for delegated admin roles with specific permissions,
            # we'd do it here by checking the admins table.
            
            return False
