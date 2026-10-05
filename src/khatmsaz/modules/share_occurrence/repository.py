"""Occurrence persistence and row locks; transactions belong to the caller."""

from sqlalchemy import select, func, or_
from sqlalchemy.dialects.postgresql import insert

from khatmsaz.core.ids import new_id
from khatmsaz.modules.share_occurrence.models import ShareMessage, ShareOccurrence


async def get(session, occurrence_id, *, for_update=False):
    stmt = select(ShareOccurrence).where(ShareOccurrence.id == occurrence_id)
    if for_update:
        stmt = stmt.with_for_update().execution_options(populate_existing=True)
    return (await session.execute(stmt)).scalar_one_or_none()


async def get_by_source(session, participation_id, source_key):
    return (await session.execute(select(ShareOccurrence).where(
        ShareOccurrence.participation_id == participation_id,
        ShareOccurrence.source_key == source_key,
    ))).scalar_one_or_none()


async def has_any(session, participation_id):
    return (await session.execute(select(ShareOccurrence.id).where(
        ShareOccurrence.participation_id == participation_id,
    ).limit(1))).scalar_one_or_none() is not None


async def list_legacy_portions(session, participation_id):
    from sqlalchemy import cast, String
    from khatmsaz.modules.allocation.models import KhatmPortion
    linked = select(ShareOccurrence.id).where(
        ShareOccurrence.participation_id == participation_id,
        ShareOccurrence.content_spec["portion_ids"].op("@>")(func.jsonb_build_array(cast(KhatmPortion.id, String))),
    ).exists()
    return list((await session.execute(select(KhatmPortion).where(
        KhatmPortion.participation_id == participation_id, KhatmPortion.status == "ASSIGNED",
        KhatmPortion.unit_kind == "POSITIONAL", ~linked,
    ).order_by(KhatmPortion.created_at, KhatmPortion.sequence))).scalars())


async def get_portion(session, portion_id, *, for_update=False):
    from khatmsaz.modules.allocation.models import KhatmPortion
    stmt = select(KhatmPortion).where(KhatmPortion.id == portion_id)
    if for_update:
        stmt = stmt.with_for_update().execution_options(populate_existing=True)
    return (await session.execute(stmt)).scalar_one_or_none()


async def create_once(session, **values):
    stmt = insert(ShareOccurrence).values(id=new_id(), **values).on_conflict_do_nothing(
        constraint="uq_share_occurrence_source",
    ).returning(ShareOccurrence.id)
    created_id = (await session.execute(stmt)).scalar_one_or_none()
    if created_id is not None:
        return await get(session, created_id), True
    stmt = select(ShareOccurrence).where(
        ShareOccurrence.participation_id == values["participation_id"],
        ShareOccurrence.source_key == values["source_key"],
    )
    return (await session.execute(stmt)).scalar_one(), False


async def add_message_once(session, **values):
    stmt = insert(ShareMessage).values(id=new_id(), **values).on_conflict_do_nothing(
        constraint="uq_share_message_component",
    ).returning(ShareMessage.id)
    created_id = (await session.execute(stmt)).scalar_one_or_none()
    stmt = select(ShareMessage).where(
        ShareMessage.occurrence_id == values["occurrence_id"],
        ShareMessage.component_key == values["component_key"],
    )
    return (await session.execute(stmt)).scalar_one(), created_id is not None


async def list_messages(session, occurrence_id):
    stmt = select(ShareMessage).where(ShareMessage.occurrence_id == occurrence_id).order_by(ShareMessage.sent_at, ShareMessage.id)
    return list((await session.execute(stmt)).scalars())


async def pending_cleanup_ids(session, *, limit=200):
    stmt = select(ShareOccurrence.id).join(ShareMessage).where(
        ShareOccurrence.completed_at.is_not(None), ShareMessage.purpose != "CONTENT",
        ShareMessage.deleted_at.is_(None),
    ).distinct().order_by(ShareOccurrence.id).limit(limit)
    return list((await session.execute(stmt)).scalars())


async def mark_delivered(session, occurrence, when):
    occurrence.delivered_at = when
    await session.flush()


async def mark_completed(session, occurrence, when):
    occurrence.completed_at = when
    await session.flush()


async def mark_message_deleted(session, message, when):
    message.deleted_at = when
    await session.flush()


async def list_outstanding(session, participation_id):
    from khatmsaz.modules.open_contribution.models import OpenReservation
    stmt = select(ShareOccurrence).outerjoin(OpenReservation, ShareOccurrence.reservation_id == OpenReservation.id).where(
        ShareOccurrence.participation_id == participation_id,
        ShareOccurrence.completed_at.is_(None),
        or_(ShareOccurrence.reservation_id.is_(None),
            (OpenReservation.status == "ACTIVE") & (OpenReservation.expires_at > func.now())),
    ).order_by(ShareOccurrence.scheduled_for, ShareOccurrence.id)
    return list((await session.execute(stmt)).scalars())
