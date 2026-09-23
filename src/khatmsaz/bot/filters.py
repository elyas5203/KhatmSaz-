from typing import Any, Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

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
        if isinstance(event, Message):
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery) and event.message:
            chat_id = event.message.chat.id
            
        if not chat_id:
            return False

        async with session_scope() as session:
            user = await identity_service.find_by_platform(session, platform, str(chat_id))
            if user is None:
                return False
                
            if user.role == UserRole.SUPER_ADMIN:
                return True
                
            # TODO: If we want to check for delegated admin roles with specific permissions,
            # we'd do it here by checking the admins table.
            
            return False
