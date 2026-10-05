"""Identity, delivery evidence and atomic completion for one exact share.

Shared by the member handlers and scheduler. Callers must keep this module
and their progress writer in the SAME database transaction.
No messenger API calls are made while holding an occurrence's completion lock.
"""

from datetime import datetime, timezone

from khatmsaz.modules.bot_registry import service as bot_registry_service
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.share_occurrence import repository


class OccurrenceAccessError(ValueError):
    pass


class OccurrenceConflictError(ValueError):
    pass


def _aware(value):
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Occurrence timestamps require a timezone")
    return value


async def create_once(
    session, *, participation_id, bot_instance_id, source_key, amount, unit,
    committed, scheduled_for, deadline_at=None, content_spec=None,
    reservation_id=None,
):
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        raise ValueError("Occurrence amount must be a positive integer")
    if unit not in {"PAGE", "COUNT", "REPETITION"} or not source_key or len(source_key) > 80:
        raise ValueError("Invalid occurrence unit or source key")
    _aware(scheduled_for)
    if deadline_at is not None:
        _aware(deadline_at)
    participation = await participation_service.get_by_id(session, participation_id)
    if participation is None or participation.status != "ACTIVE" or participation.joined_via_bot_instance_id != bot_instance_id or bot_instance_id is None:
        raise OccurrenceAccessError("A matching member-bot route is required")
    bot = await bot_registry_service.get_instance(session, bot_instance_id)
    if bot is None or bot.bot_role != "MEMBER" or not bot.is_active:
        raise OccurrenceAccessError("An active member bot is required")
    values = dict(
        participation_id=participation_id, bot_instance_id=bot_instance_id,
        source_key=source_key, amount=amount, unit=unit, committed=committed,
        scheduled_for=scheduled_for, deadline_at=deadline_at, content_spec=content_spec or {},
        reservation_id=reservation_id,
    )
    occurrence, created = await repository.create_once(session, **values)
    if not created and any(getattr(occurrence, key) != value for key, value in values.items()):
        raise OccurrenceConflictError("An existing share's payload cannot be replaced")
    return occurrence, created


async def record_message(
    session, *, occurrence_id, bot_instance_id, component_key, purpose, chat_id, message_id, sent_at,
):
    _aware(sent_at)
    if purpose not in {"CONTENT", "ACTION", "FOLLOWUP", "DEADLINE"} or not component_key or len(component_key) > 80:
        raise ValueError("Invalid message component")
    if message_id <= 0 or not str(chat_id) or len(str(chat_id)) > 32:
        raise ValueError("Invalid message receipt")
    occurrence = await repository.get(session, occurrence_id, for_update=True)
    if occurrence is None or occurrence.bot_instance_id != bot_instance_id:
        raise OccurrenceAccessError("Message route does not own this share")
    existing = await repository.list_messages(session, occurrence_id)
    if any(item.chat_id != str(chat_id) for item in existing):
        raise OccurrenceAccessError("All share components must belong to the same chat")
    values = dict(
        occurrence_id=occurrence_id, component_key=component_key, purpose=purpose,
        chat_id=str(chat_id), message_id=message_id, sent_at=sent_at,
    )
    message, created = await repository.add_message_once(session, **values)
    if not created and any(getattr(message, key) != values[key] for key in ("purpose", "chat_id", "message_id")):
        raise OccurrenceConflictError("A recorded message cannot be silently replaced")
    return message


async def mark_delivered(session, occurrence_id, *, bot_instance_id, when=None):
    occurrence = await repository.get(session, occurrence_id, for_update=True)
    if occurrence is None or occurrence.bot_instance_id != bot_instance_id:
        raise OccurrenceAccessError("Delivery route does not own this share")
    if occurrence.delivered_at is not None:
        return occurrence
    messages = await repository.list_messages(session, occurrence_id)
    if not {"CONTENT", "ACTION"} <= {message.purpose for message in messages}:
        raise ValueError("Content and action receipts are required before delivery")
    await repository.mark_delivered(session, occurrence, _aware(when or datetime.now(timezone.utc)))
    return occurrence


async def complete(session, occurrence_id, *, user_id, bot_instance_id, record_progress, when=None):
    """Return (occurrence, newly_completed); progress writer is DB-only.

    ``record_progress(session, participation, occurrence)`` must not commit or
    send messages. It supplies the domain-specific Quran/count goal accounting
    at cutover. Its failure rolls back with the caller; retries cannot complete
    another occurrence or count this one twice.
    """
    occurrence = await repository.get(session, occurrence_id, for_update=True)
    if occurrence is None or occurrence.bot_instance_id != bot_instance_id:
        raise OccurrenceAccessError("Unknown share or wrong member bot")
    participation = await participation_service.get_by_id(session, occurrence.participation_id)
    if participation is None or participation.user_id != user_id:
        raise OccurrenceAccessError("Only the owning member may complete a share")
    if occurrence.completed_at is not None:
        return occurrence, False
    if occurrence.delivered_at is None:
        raise OccurrenceAccessError("An undelivered share cannot be completed")
    if occurrence.reservation_id is not None:
        from khatmsaz.modules.open_contribution import repository as reservations
        reservation = await reservations.get_reservation(session, occurrence.reservation_id, for_update=True)
        if reservation is None or reservation.status != "ACTIVE" or reservation.expires_at <= (when or datetime.now(timezone.utc)):
            raise OccurrenceAccessError("Reservation expired or is no longer active")
        reservation.status = "COMPLETED"
    completed_at = _aware(when or datetime.now(timezone.utc))
    await record_progress(session, participation, occurrence)
    await repository.mark_completed(session, occurrence, completed_at)
    return occurrence, True


async def cleanup_candidates(session, occurrence_id):
    """Only completed shares' non-content receipts can be removed."""
    occurrence = await repository.get(session, occurrence_id)
    if occurrence is None or occurrence.completed_at is None:
        return []
    return [
        message for message in await repository.list_messages(session, occurrence_id)
        if message.purpose != "CONTENT" and message.deleted_at is None
    ]


async def record_message_deleted(session, occurrence_id, message_id, *, when=None):
    candidates = await cleanup_candidates(session, occurrence_id)
    message = next((item for item in candidates if item.id == message_id), None)
    if message is None:
        return False
    await repository.mark_message_deleted(session, message, _aware(when or datetime.now(timezone.utc)))
    return True


async def list_outstanding(session, participation_id):
    return await repository.list_outstanding(session, participation_id)


async def complete_legacy_portion(session, portion_id, *, user_id, bot_instance_id):
    """Keep historical debt actionable without inventing delivery receipts."""
    from khatmsaz.modules.khatm import service as khatms
    from khatmsaz.modules.allocation import repository as portions
    portion = await repository.get_portion(session, portion_id)
    if portion is None:
        raise OccurrenceAccessError("Unknown legacy portion")
    part = await participation_service.get_by_id(session, portion.participation_id)
    if part is None or part.user_id != user_id or bot_instance_id is None or part.joined_via_bot_instance_id != bot_instance_id:
        raise OccurrenceAccessError("This portion belongs to another member bot")
    await khatms.get_khatm_for_update(session, part.khatm_id)
    portion = await repository.get_portion(session, portion_id, for_update=True)
    if portion.status == "COMPLETED":
        return False
    if portion.id not in {p.id for p in await repository.list_legacy_portions(session, part.id)}:
        raise ValueError("Use the exact share action")
    await portions.complete_portion(session, portion_id)
    return True
