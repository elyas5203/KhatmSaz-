"""Best-effort push notifications for queues that require admin action."""

from khatmsaz.bot.admin_sync import get_all_admin_telegram_chat_ids
from khatmsaz.bot.notify_adapter import get_notify_fn
from khatmsaz.modules.identity.models import Platform


async def notify_admins(text: str) -> None:
    """Notify all configured and delegated admins on Telegram."""
    admin_ids = await get_all_admin_telegram_chat_ids()
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


async def notify_super_admins(text: str) -> None:
    """Backward-compatible alias for notifying administrators."""
    await notify_admins(text)
