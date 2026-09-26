"""Identity orchestration: resolve-or-provision a User from a platform chat,
plus admin moderation (ban/warn) and the super-admin bootstrap.

This is the one entry point bot handlers use to turn "a Telegram/Bale chat
just messaged us" into a canonical User. It never creates a duplicate user
for a chat id that is already linked (idempotent by construction — the
(platform, subject) unique constraint is the backstop).
"""

from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.config import get_settings
from khatmsaz.modules.identity import repository
from khatmsaz.modules.identity.models import Platform, PlatformIdentity, User, UserRole, UserStatus
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.settings.models import UserSettings
from khatmsaz.modules.waiting_list.models import WaitingList


class AccountDeletionBlocked(Exception):
    """The account still owns an obligation that must be resolved first."""

    def __init__(self, *, committed_count: int = 0, active_created_count: int = 0):
        self.committed_count = committed_count
        self.active_created_count = active_created_count
        super().__init__("account deletion is blocked by active obligations")


async def resolve_or_provision_user(session: AsyncSession, platform: Platform, chat_id: int) -> User:
    subject = str(chat_id)
    existing = await repository.find_by_platform_identity(session, platform, subject)
    if existing is not None:
        user = existing
    else:
        try:
            user = await repository.create_user_with_platform_identity(session, platform, subject)
        except IntegrityError:
            # Lost a race: a concurrent request for the same (platform, subject)
            # committed first (e.g. Telegram delivering several queued updates
            # from the same chat at once). Our own insert was rolled back
            # (see repository.py's SAVEPOINT) — the winner's row is there now.
            winner = await repository.find_by_platform_identity(session, platform, subject)
            if winner is None:
                raise
            user = winner

    await _bootstrap_super_admin_if_configured(session, platform, subject, user)
    return user


async def _bootstrap_super_admin_if_configured(
    session: AsyncSession, platform: Platform, subject: str, user: User
) -> None:
    """No admin panel exists yet, so the very first admin has to be granted
    somehow — DECISIONS.md DEC-PY-0013: whoever's Telegram chat id is listed
    in `SUPER_ADMIN_TELEGRAM_CHAT_IDS` gets promoted automatically the next
    time they message the bot. A no-op for everyone else, every time."""
    if user.role == UserRole.SUPER_ADMIN:
        return
    settings = get_settings()
    if platform == Platform.TELEGRAM:
        raw_ids = settings.super_admin_telegram_chat_ids
    elif platform == Platform.BALE:
        raw_ids = settings.super_admin_bale_chat_ids
    else:
        return
    admin_ids = {s.strip() for s in raw_ids.split(",") if s.strip()}
    if subject in admin_ids:
        await repository.set_role(session, user.id, UserRole.SUPER_ADMIN)
        user.role = UserRole.SUPER_ADMIN


async def list_identities_for_user(session: AsyncSession, user_id: str) -> list[PlatformIdentity]:
    return await repository.list_platform_identities(session, user_id)


async def is_blocked(user: User) -> bool:
    return user.deleted_at is not None or user.status in (UserStatus.SUSPENDED, UserStatus.BANNED)


async def warn(session: AsyncSession, user_id) -> None:
    await repository.set_status(session, user_id, UserStatus.WARNED)


async def suspend(session: AsyncSession, user_id) -> None:
    await repository.set_status(session, user_id, UserStatus.SUSPENDED)


async def ban(session: AsyncSession, user_id) -> None:
    await repository.set_status(session, user_id, UserStatus.BANNED)


async def reactivate(session: AsyncSession, user_id) -> None:
    await repository.set_status(session, user_id, UserStatus.ACTIVE)


async def find_by_platform(session: AsyncSession, platform: Platform, chat_id: str) -> User | None:
    return await repository.find_by_platform_identity(session, platform, chat_id)


async def find_by_id(session: AsyncSession, user_id) -> User | None:
    return await repository.find_by_id(session, user_id)


async def search_users(
    session: AsyncSession, query: str, *, limit: int = 10, offset: int = 0
) -> list[User]:
    return await repository.search_users(session, query, limit=limit, offset=offset)


async def set_display_name(session: AsyncSession, user_id, display_name: str) -> None:
    await repository.set_display_name(session, user_id, display_name)


async def delete_account(session: AsyncSession, user_id) -> None:
    """Safely deactivate a user while retaining non-PII history.

    Active committed participation must be left/fulfilled first. Active
    khatms created by the user are also blocked so members never lose their
    creator unexpectedly. Open memberships are closed automatically because
    they carry no protected commitment.
    """
    committed_result = await session.execute(
        select(func.count())
        .select_from(Participation)
        .where(
            Participation.user_id == user_id,
            Participation.status == ParticipationStatus.ACTIVE,
            Participation.is_committed.is_(True),
        )
    )
    committed_count = int(committed_result.scalar_one())

    created_result = await session.execute(
        select(func.count())
        .select_from(Khatm)
        .where(Khatm.creator_user_id == user_id, Khatm.status == KhatmStatus.ACTIVE)
    )
    active_created_count = int(created_result.scalar_one())
    if committed_count or active_created_count:
        raise AccountDeletionBlocked(
            committed_count=committed_count, active_created_count=active_created_count
        )

    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(Participation).where(
            Participation.user_id == user_id, Participation.status == ParticipationStatus.ACTIVE
        )
    )
    for participation in result.scalars():
        participation.status = ParticipationStatus.LEFT
        participation.leave_reason = "ACCOUNT_DELETED"

    await session.execute(delete(WaitingList).where(WaitingList.user_id == user_id))
    user = await session.get(User, user_id)
    if user is None:
        return
    user.deleted_at = now
    user.display_name = None
    settings = await session.get(UserSettings, user_id)
    if settings is not None:
        settings.contact_phone = None
        settings.city = None
        settings.province = None
        settings.gender = None
        settings.sms_enabled = False

async def promote_creator(session: AsyncSession, user_id) -> None:
    user = await find_by_id(session, user_id)
    if user and user.role != UserRole.SUPER_ADMIN:
        user.role = UserRole.CREATOR

async def demote_creator(session: AsyncSession, user_id) -> None:
    user = await find_by_id(session, user_id)
    if user and user.role != UserRole.SUPER_ADMIN:
        user.role = UserRole.USER
