from sqlalchemy.ext.asyncio import AsyncSession

from khatmsaz.modules.khatm_category import repository
from khatmsaz.modules.khatm_category.models import (
    KhatmCategory,
    KhatmCategoryGroup,
    KhatmCategoryRequest,
    KhatmCategoryRequestStatus,
)


async def list_active(
    session: AsyncSession, group: KhatmCategoryGroup | str | None = None
) -> list[KhatmCategory]:
    if isinstance(group, str):
        try:
            group = KhatmCategoryGroup(group)
        except ValueError:
            raise ValueError("unsupported category group") from None
    return await repository.list_active(session, group)


async def list_all(session: AsyncSession) -> list[KhatmCategory]:
    return await repository.list_all(session)


async def get(session: AsyncSession, category_id) -> KhatmCategory | None:
    return await repository.get_by_id(session, category_id)


async def create(
    session: AsyncSession, *, group: str, title: str, body_text: str | None, source_note: str | None,
    devotional_slug: str | None = None, image_url: str | None = None,
) -> KhatmCategory:
    title = title.strip()
    if not title:
        raise ValueError("category title is required")
    try:
        group_enum = KhatmCategoryGroup(group)
    except ValueError:
        raise ValueError("unsupported category group") from None
    return await repository.create(
        session, group=group_enum, title=title, body_text=(body_text or "").strip() or None,
        source_note=(source_note or "").strip() or None,
        devotional_slug=(devotional_slug or "").strip().lower() or None,
        image_url=(image_url or "").strip() or None,
    )


async def update(
    session: AsyncSession, category_id, *, title: str, body_text: str | None, source_note: str | None,
    devotional_slug: str | None = None, image_url: str | None = None,
) -> KhatmCategory:
    category = await repository.get_by_id(session, category_id)
    if category is None:
        raise ValueError("category not found")
    title = title.strip()
    if not title:
        raise ValueError("category title is required")
    return await repository.update(
        session, category, title=title, body_text=(body_text or "").strip() or None,
        source_note=(source_note or "").strip() or None,
        devotional_slug=(devotional_slug or "").strip().lower() or None,
        image_url=(image_url or "").strip() or None,
    )


async def set_active(session: AsyncSession, category_id, active: bool) -> KhatmCategory:
    category = await repository.get_by_id(session, category_id)
    if category is None:
        raise ValueError("category not found")
    return await repository.set_active(session, category, active)


async def submit_request(session: AsyncSession, *, requested_title: str, requested_by_user_id) -> KhatmCategoryRequest:
    requested_title = requested_title.strip()
    if not requested_title or len(requested_title) > 200:
        raise ValueError("request title must be between 1 and 200 characters")
    return await repository.create_request(
        session, requested_title=requested_title, requested_by_user_id=requested_by_user_id
    )


async def list_pending_requests(session: AsyncSession) -> list[KhatmCategoryRequest]:
    return await repository.list_pending_requests(session)


async def fulfill_request(
    session: AsyncSession, request_id, *, group: str, title: str, body_text: str | None, source_note: str | None,
    image_url: str | None = None, devotional_slug: str | None = None,
) -> tuple[KhatmCategoryRequest, KhatmCategory]:
    request = await repository.get_request_by_id(session, request_id)
    if request is None:
        raise ValueError("request not found")
    if request.status != KhatmCategoryRequestStatus.PENDING:
        raise ValueError("request is not pending")
    category = await create(
        session, group=group, title=title, body_text=body_text, source_note=source_note,
        image_url=image_url, devotional_slug=devotional_slug,
    )
    request = await repository.mark_request_fulfilled(session, request, category)
    return request, category


async def decline_request(session: AsyncSession, request_id) -> KhatmCategoryRequest:
    request = await repository.get_request_by_id(session, request_id)
    if request is None:
        raise ValueError("request not found")
    if request.status != KhatmCategoryRequestStatus.PENDING:
        raise ValueError("request is not pending")
    return await repository.mark_request_declined(session, request)
