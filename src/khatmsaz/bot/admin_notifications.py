"""Best-effort push notifications for queues that require admin action."""

from khatmsaz.bot.notify_adapter import get_notify_fn
from khatmsaz.config import get_settings
from khatmsaz.modules.identity.models import Platform


async def notify_super_admins(text: str) -> None:
    admin_ids = [
        value.strip()
        for value in get_settings().super_admin_telegram_chat_ids.split(",")
        if value.strip()
    ]
    try:
        notify = get_notify_fn()
    except RuntimeError:
        return
    for chat_id in admin_ids:
        try:
            await notify(Platform.TELEGRAM.value, chat_id, text)
        except Exception:
            # Queue persistence is authoritative; a temporary delivery failure
            # must not reject or duplicate the user's submitted request.
            pass
