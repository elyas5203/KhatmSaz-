from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.core.ids import new_id
from khatmsaz.modules.khatm_category.models import (
    KhatmCategory,
    KhatmCategoryGroup,
    KhatmCategoryRequest,
    KhatmCategoryRequestStatus,
)


async def list_active(
    session: AsyncSession, group: KhatmCategoryGroup | None = None
) -> list[KhatmCategory]:
    stmt = (
        select(KhatmCategory)
        .where(KhatmCategory.is_active.is_(True))
        .order_by(KhatmCategory.group, KhatmCategory.sort_order, KhatmCategory.title)
    )
    if group is not None:
        stmt = stmt.where(KhatmCategory.group == group)
    return list((await session.execute(stmt)).scalars().all())


async def list_all(session: AsyncSession) -> list[KhatmCategory]:
    stmt = select(KhatmCategory).order_by(KhatmCategory.group, KhatmCategory.sort_order, KhatmCategory.title)
    return list((await session.execute(stmt)).scalars().all())


async def get_by_id(session: AsyncSession, category_id) -> KhatmCategory | None:
    return await session.get(KhatmCategory, category_id)


async def create(
    session: AsyncSession, *, group: KhatmCategoryGroup, title: str, body_text: str | None, source_note: str | None,
    devotional_slug: str | None = None, image_url: str | None = None, sort_order: int = 0,
) -> KhatmCategory:
    category = KhatmCategory(
        id=new_id(), group=group, title=title.strip(), body_text=body_text, source_note=source_note,
        devotional_slug=devotional_slug, image_url=image_url, sort_order=sort_order,
    )
    session.add(category)
    await session.flush()
    return category


async def update(
    session: AsyncSession, category: KhatmCategory, *, title: str, body_text: str | None, source_note: str | None,
    devotional_slug: str | None = None, image_url: str | None = None, sort_order: int = 0,
) -> KhatmCategory:
    category.title = title.strip()
    category.body_text = body_text
    category.source_note = source_note
    category.devotional_slug = devotional_slug
    category.image_url = image_url
    category.sort_order = sort_order
    await session.flush()
    return category


async def set_active(session: AsyncSession, category: KhatmCategory, active: bool) -> KhatmCategory:
    category.is_active = active
    await session.flush()
    return category


async def set_sort_orders(
    session: AsyncSession, ordered_categories: list[KhatmCategory]
) -> None:
    """Persist a dense wizard order; gaps/duplicates never leak to the UI."""
    for index, category in enumerate(ordered_categories, start=1):
        category.sort_order = index
    await session.flush()


async def list_pending_requests(session: AsyncSession) -> list[KhatmCategoryRequest]:
    stmt = (
        select(KhatmCategoryRequest)
        .where(KhatmCategoryRequest.status == KhatmCategoryRequestStatus.PENDING)
        .order_by(KhatmCategoryRequest.created_at)
    )
    return list((await session.execute(stmt)).scalars().all())


async def create_request(session: AsyncSession, *, requested_title: str, requested_by_user_id) -> KhatmCategoryRequest:
    request = KhatmCategoryRequest(
        id=new_id(), requested_title=requested_title.strip(), requested_by_user_id=requested_by_user_id
    )
    session.add(request)
    await session.flush()
    return request


async def get_request_by_id(session: AsyncSession, request_id) -> KhatmCategoryRequest | None:
    return await session.get(KhatmCategoryRequest, request_id)


async def mark_request_fulfilled(
    session: AsyncSession, request: KhatmCategoryRequest, category: KhatmCategory
) -> KhatmCategoryRequest:
    request.status = KhatmCategoryRequestStatus.FULFILLED
    request.fulfilled_category_id = category.id
    await session.flush()
    return request


async def mark_request_declined(session: AsyncSession, request: KhatmCategoryRequest) -> KhatmCategoryRequest:
    request.status = KhatmCategoryRequestStatus.DECLINED
    await session.flush()
    return request
