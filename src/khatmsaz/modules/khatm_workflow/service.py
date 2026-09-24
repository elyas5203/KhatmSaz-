"""Cross-module orchestration for the khatm creation wizard, join/leave flow,
and waiting-list promotion.

This is the one place allowed to call more than one module's `service.py` in
sequence (see ARCHITECTURE.md's isolation rule) — everything else should go
through exactly one module's service.

Commitment mode (COMMITMENT vs OPEN) is an explicit creator choice made
independently of the content template (DOMAIN_MODEL.md §2; DEC-PY-0007
supersedes the earlier per-template hard-wiring, DEC-PY-0004). Four
combinations exist today:
  - QURAN_PAGE + COMMITMENT: sequential personal-journey page assignment,
    optionally capacity-limited with a waiting list (DEC-PY-0010).
  - QURAN_PAGE + OPEN: no page assignment; participants freely log how many
    pages they read, same "mazad" overflow accounting as Salawat, target =
    the chosen edition's total page count.
  - SALAWAT + COMMITMENT: every participant is assigned the same fixed
    quantity the creator set (e.g. "everyone commits to 1000"); supports
    chunked partial logging and one-tap completion. Also supports an
    optional capacity + waiting list, same as QURAN_PAGE (DEC-PY-0010,
    extended 2026-09-20): a waitlisted participant contributes casually
    through the open pool while waiting for a committed slot.
  - SALAWAT + OPEN: free-form logging against a shared target pool (Phase 1
    behavior, unchanged).
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from khatmsaz.modules.allocation import service as allocation_service
from khatmsaz.modules.allocation.models import KhatmPortion
from khatmsaz.modules.invitation import service as invitation_service
from khatmsaz.modules.khatm import service as khatm_service
from khatmsaz.modules.khatm.models import ContentDeliveryMode, CreatorDisplayMode, Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum, KhatmVisibility, ReminderTone
from khatmsaz.modules.khatm.quran_editions import QURAN_EDITIONS
from khatmsaz.modules.content.service import CANONICAL_EDITION_ID
from khatmsaz.modules.content.quran_channel_seed import AUDIO_MESSAGE_RANGES
from khatmsaz.modules.participation import service as participation_service
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.modules.participation.service import AlreadyParticipatingError
from khatmsaz.modules.plan import service as plan_service
from khatmsaz.modules.plan.models import PlanTier
from khatmsaz.modules.wallet import service as wallet_service
from khatmsaz.modules.wallet.models import InvoiceKind
from khatmsaz.modules.waiting_list import service as waiting_list_service


class PlanCapExceededError(Exception):
    """Raised when a FREE-tier creator has hit their member cap and tries to
    create another khatm (DEC-PY-0074). Existing khatms/members are never
    touched — only new khatm creation is blocked."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


_QURAN_TEMPLATE_TYPES = {
    KhatmTemplateType.QURAN_PAGE,
    KhatmTemplateType.QURAN_SURAH,
    KhatmTemplateType.SURAH,
}
_DEVOTIONAL_TEMPLATE_TYPES = {
    KhatmTemplateType.SALAWAT,
    KhatmTemplateType.DUA,
    KhatmTemplateType.ZIYARAT,
    KhatmTemplateType.CUSTOM,
}


async def _count_creator_members(session: AsyncSession, creator_user_id, template_type: KhatmTemplateType) -> int:
    family_types = (
        _QURAN_TEMPLATE_TYPES
        if template_type in _QURAN_TEMPLATE_TYPES
        else _DEVOTIONAL_TEMPLATE_TYPES
    )
    stmt = (
        select(func.count())
        .select_from(Participation)
        .join(Khatm, Khatm.id == Participation.khatm_id)
        .where(
            Khatm.creator_user_id == creator_user_id,
            Khatm.template_type.in_(family_types),
            Participation.status == ParticipationStatus.ACTIVE,
        )
    )
    return int((await session.execute(stmt)).scalar_one())


async def _enforce_creation_cap(session: AsyncSession, creator_user_id, template_type: KhatmTemplateType) -> None:
    """DEC-PY-0074: a FREE-tier creator's member cap is summed across all
    their own SALAWAT-family (صلوات/دعا/زیارت/لعن) khatms, and separately
    for QURAN_PAGE. A paid plan (anything above FREE) is never capped here.
    A missing/disabled plan definition means unlimited, matching the
    existing fallback rule in `plan_service.get_creation_price`."""
    if await plan_service.get_plan(session, creator_user_id) != PlanTier.FREE:
        return
    definition = await plan_service.get_definition(session, PlanTier.FREE)
    if definition is None or not definition.enabled:
        return
    if template_type in _QURAN_TEMPLATE_TYPES:
        cap = definition.entitlements.get("max_quran_members")
    else:
        cap = definition.entitlements.get("max_devotional_members")
    if cap is None:
        return
    current = await _count_creator_members(session, creator_user_id, template_type)
    if current >= int(cap):
        raise PlanCapExceededError(
            "شما به سقف مجاز پلن رایگان رسیده‌اید؛ برای ساخت ختم جدید باید یک پلن/اشتراک بخرید. "
            "ختم‌ها و اعضای فعلی شما تغییری نمی‌کنند."
        )


class JoinRequiresApprovalError(Exception):
    """Raised by `join_via_token` for a PRIVATE khatm (DOMAIN_MODEL.md §2
    Q65-66) the caller isn't already a member of — nothing is created yet;
    the bot handler notifies the creator and calls `approve_join_request`
    only if they approve. Carries the khatm so the handler doesn't need a
    second lookup."""

    def __init__(self, khatm: Khatm):
        self.khatm = khatm
        super().__init__(f"khatm {khatm.id} requires creator approval to join")


class InvalidCreatorDecisionError(Exception):
    """The requested missed-commitment resolution is not applicable."""


class KhatmCancellationError(Exception):
    """A khatm cannot be cancelled/refunded under the current rules."""


class KhatmUnavailableError(Exception):
    """A completed or cancelled khatm cannot accept new members/work."""


async def create_and_launch_khatm(
    session: AsyncSession,
    *,
    creator_user_id,
    template_type: KhatmTemplateType,
    khatm_type: KhatmTypeEnum,
    title: str,
    niyyat: str | None,
    welcome_text: str | None = None,
    salawat_open_target: int | None = None,
    salawat_commitment_quantity: int | None = None,
    quran_edition_id: str | None = None,
    daily_deadline_hour: int | None = None,
    capacity: int | None = None,
    allow_skip_today: bool = True,
    allow_pause: bool = True,
    allow_snooze: bool = True,
    completion_announcement_enabled: bool = True,
    miss_notice_threshold: int = 2,
    miss_notice_window_days: int = 3,
    schedule_kind: str = "NONE",
    schedule_value: str | None = None,
    visibility: KhatmVisibility = KhatmVisibility.UNLISTED,
    allowed_platforms: str = "BOTH",
    pages_per_portion: int = allocation_service.DEFAULT_PAGES_PER_PORTION,
    creation_price_toman: int = 0,
    advertising_enabled: bool = False,
    content_delivery_mode: ContentDeliveryMode | str = ContentDeliveryMode.AUTO,
    reminder_tone: ReminderTone | str = ReminderTone.FRIENDLY,
    creator_display_mode: CreatorDisplayMode | str = CreatorDisplayMode.FULL_NAME,
    creator_pseudonym: str | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    coupon_code: str | None = None,
    content_category_id=None,
    description: str | None = None,
) -> tuple[Khatm, str]:
    """`creation_price_toman` (DOMAIN_MODEL.md §7: creating a khatm costs
    money, joining is free) is charged from the creator's wallet — credit
    first, then real balance — *before* anything is created, so a failed
    charge never leaves a half-created khatm. Raises
    `wallet.service.InsufficientFundsError` if they can't afford it. Pass 0
    (the default while no payment gateway is live — DEC-PY-0012) to skip
    charging entirely."""
    await _enforce_creation_cap(session, creator_user_id, template_type)
    purchase_invoice = None
    if creation_price_toman > 0:
        purchase_invoice = await wallet_service.purchase(
            session,
            user_id=creator_user_id,
            gross_amount_toman=creation_price_toman,
            description=f"ساخت ختم: {title}",
            invoice_kind=InvoiceKind.KHATM_CREATION,
            coupon_code=coupon_code,
        )
    charged_price_toman = (
        purchase_invoice.net_amount_toman if purchase_invoice is not None else 0
    )

    extra: dict = {}
    display_mode = CreatorDisplayMode(
        creator_display_mode.upper() if isinstance(creator_display_mode, str) else creator_display_mode
    )
    if display_mode == CreatorDisplayMode.PSEUDONYM and not (creator_pseudonym or "").strip():
        raise ValueError("pseudonym is required when creator display mode is PSEUDONYM")
    if display_mode != CreatorDisplayMode.PSEUDONYM:
        creator_pseudonym = None
    extra["creator_display_mode"] = display_mode.value
    extra["creator_pseudonym"] = (creator_pseudonym or "").strip() or None
    extra["reminder_tone"] = ReminderTone(
        reminder_tone.upper() if isinstance(reminder_tone, str) else reminder_tone
    ).value

    if template_type == KhatmTemplateType.SALAWAT:
        if khatm_type == KhatmTypeEnum.OPEN:
            extra["repetition_target"] = salawat_open_target
        else:
            # Reused field for the other meaning: the fixed amount every
            # committed participant is assigned, not a shared pool target.
            extra["repetition_target"] = salawat_commitment_quantity
            # Capacity + waiting list also applies to SALAWAT+COMMITMENT
            # (owner decision, 2026-09-20): a waitlisted participant reads
            # along freely via the open contribution pool, same as
            # QURAN_PAGE+COMMITMENT (DEC-PY-0010).
            extra["capacity"] = capacity
        extra["content_category_id"] = content_category_id
    elif template_type == KhatmTemplateType.QURAN_PAGE:
        extra["quran_edition_id"] = quran_edition_id
        extra["content_delivery_mode"] = ContentDeliveryMode(
            content_delivery_mode.upper() if isinstance(content_delivery_mode, str) else content_delivery_mode
        ).value
        if khatm_type == KhatmTypeEnum.OPEN:
            extra["repetition_target"] = QURAN_EDITIONS[quran_edition_id]["total_pages"]
        else:
            # Only QURAN_PAGE + COMMITMENT has these concepts today (DEC-PY-0008/0010).
            extra["daily_deadline_hour"] = daily_deadline_hour
            extra["capacity"] = capacity
            extra["allow_skip_today"] = allow_skip_today

    khatm = await khatm_service.create_draft_khatm(
        session,
        creator_user_id=creator_user_id,
        title=title,
        template_type=template_type,
        khatm_type=khatm_type,
        niyyat=niyyat,
        welcome_text=welcome_text,
        # Owner request (2026-09-21): a creator making a SALAWAT-family
        # khatm (especially a custom La'an/Dua) can write out the actual
        # recitation text; it's sent to members alongside their portion/
        # contribution confirmation (see portions.py). Repurposes the
        # pre-existing, previously-unused `Khatm.description` column
        # instead of a new migration.
        description=(description or "").strip() or None,
        creation_price_toman=charged_price_toman,
        advertising_enabled=advertising_enabled,
        allow_pause=allow_pause,
        allow_snooze=allow_snooze,
        completion_announcement_enabled=completion_announcement_enabled,
        miss_notice_threshold=miss_notice_threshold,
        miss_notice_window_days=miss_notice_window_days,
        schedule_kind=schedule_kind,
        schedule_value=schedule_value,
        visibility=visibility,
        allowed_platforms=allowed_platforms,
        **extra,
        start_at=start_at,
        end_at=end_at,
    )

    if purchase_invoice is not None:
        await wallet_service.bind_invoice_resource(
            session, purchase_invoice.id, str(khatm.id)
        )

    if template_type == KhatmTemplateType.QURAN_PAGE and khatm_type == KhatmTypeEnum.COMMITMENT:
        if quran_edition_id == CANONICAL_EDITION_ID:
            # Owner-reported bug (2026-09-21): align portion boundaries with
            # the reciter's real audio-segment boundaries instead of a
            # uniform 2-pages-per-portion split starting at page 1 — the
            # audio was actually recorded as pages 1-3 combined, then pairs
            # from page 4 onward, so the old uniform split made most
            # portions straddle two different audio files (e.g. a "pages
            # 7-8" portion needed audio from both the 6-7 and 8-9 tracks).
            boundaries = [(start, end) for start, end, _ in AUDIO_MESSAGE_RANGES]
            await allocation_service.generate_quran_page_plan_from_boundaries(session, khatm.id, boundaries)
        else:
            total_pages = QURAN_EDITIONS[quran_edition_id]["total_pages"]
            await allocation_service.generate_quran_page_plan(session, khatm.id, total_pages, pages_per_portion)

    await khatm_service.activate_khatm(session, khatm.id)

    token = await invitation_service.create_invitation(session, khatm.id, creator_user_id)
    return khatm, token


async def join_via_token(
    session: AsyncSession, *, token: str, user_id
) -> tuple[Khatm | None, Participation, KhatmPortion | None, bool]:
    """Returns (khatm, participation, first_portion, was_waitlisted).
    Raises `JoinRequiresApprovalError` for a PRIVATE khatm — see that
    class's docstring."""
    khatm_id = await invitation_service.resolve_khatm_id(session, token)
    khatm = await khatm_service.get_khatm(session, khatm_id)

    if khatm is not None and khatm.visibility == KhatmVisibility.PRIVATE:
        if await participation_service.get_active(session, khatm_id, user_id) is not None:
            raise AlreadyParticipatingError()
        raise JoinRequiresApprovalError(khatm)

    return await _complete_join(session, khatm, user_id)


async def approve_join_request(
    session: AsyncSession, khatm_id, user_id, *, creator_user_id
) -> tuple[Khatm | None, Participation, KhatmPortion | None, bool]:
    """The creator approved a PRIVATE khatm's join request — actually create
    the participation now. Same return shape as `join_via_token`."""
    khatm = await khatm_service.get_khatm(session, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id:
        raise PermissionError("only the khatm creator may approve join requests")
    return await _complete_join(session, khatm, user_id)


async def _complete_join(
    session: AsyncSession, khatm: Khatm | None, user_id
) -> tuple[Khatm | None, Participation, KhatmPortion | None, bool]:
    khatm_id = khatm.id if khatm is not None else None
    if khatm is None or khatm.status != KhatmStatus.ACTIVE:
        raise KhatmUnavailableError()

    capacity = None
    if khatm is not None and khatm.khatm_type == KhatmTypeEnum.COMMITMENT and khatm.template_type in (
        KhatmTemplateType.QURAN_PAGE, KhatmTemplateType.SALAWAT,
    ):
        capacity = khatm.capacity

    participation, was_waitlisted = await participation_service.join(session, khatm_id, user_id, capacity=capacity)

    if was_waitlisted:
        await waiting_list_service.join(session, khatm_id, user_id)
        return khatm, participation, None, True

    first_portion: KhatmPortion | None = None
    if khatm is not None and khatm.khatm_type == KhatmTypeEnum.COMMITMENT:
        if khatm.template_type == KhatmTemplateType.QURAN_PAGE:
            first_portion = await allocation_service.allocate_next_portion_to(session, khatm_id, participation.id)
        elif khatm.template_type == KhatmTemplateType.SALAWAT:
            first_portion = await allocation_service.assign_quantity_commitment(
                session, khatm_id, participation.id, khatm.repetition_target
            )

    return khatm, participation, first_portion, False


async def leave_khatm(
    session: AsyncSession, participation_id, *, reason: str | None = None
) -> tuple[Participation | None, KhatmPortion | None]:
    """Leave a khatm. If the leaver was a committed participant, promote the
    next person in the waiting list (if any) into their place — a fresh
    committed participation + first portion. Returns (promoted_participation,
    promoted_first_portion), both None if nobody was waiting.

    `reason` (DOMAIN_MODEL.md §3 Q98) is a quick-pick code, stored for later
    churn analysis — never shown to the creator today."""
    participation = await participation_service.get_by_id(session, participation_id)
    if participation is None:
        return None, None

    was_committed = participation.is_committed
    await participation_service.leave(session, participation_id, reason=reason)

    if not was_committed:
        return None, None

    khatm = await khatm_service.get_khatm(session, participation.khatm_id)
    if khatm is None or khatm.capacity is None:
        return None, None

    entry = await waiting_list_service.promote_next(session, khatm.id)
    if entry is None:
        return None, None

    promoted_participation = await participation_service.get_active(session, khatm.id, entry.user_id)
    if promoted_participation is None:
        return None, None

    await participation_service.promote_to_committed(session, promoted_participation.id)

    new_portion: KhatmPortion | None = None
    if khatm.template_type == KhatmTemplateType.QURAN_PAGE:
        new_portion = await allocation_service.allocate_next_portion_to(
            session, khatm.id, promoted_participation.id
        )
    elif khatm.template_type == KhatmTemplateType.SALAWAT:
        new_portion = await allocation_service.assign_quantity_commitment(
            session, khatm.id, promoted_participation.id, khatm.repetition_target
        )

    return promoted_participation, new_portion


async def skip_today(session: AsyncSession, khatm_id, participation_id) -> bool:
    """"امروز نمی‌رسم" (DOMAIN_MODEL.md §3 Q79): proactively release today's
    portion *before* the deadline — no miss recorded, unlike a deadline
    passing untouched (reminder_engine's path). Returns False if there was
    no current portion to release (nothing to do)."""
    current = await allocation_service.get_current_portion(session, khatm_id, participation_id)
    if current is None:
        return False
    await allocation_service.release_portion(session, current.id)
    return True


async def pause_commitment(session: AsyncSession, participation_id, khatm_id, until) -> None:
    """"موقتاً متوقف کن" (DOMAIN_MODEL.md §3 Q80): release any current
    portion (same as skip_today — no miss) and mark the participation
    paused until `until`. `reminder_engine` and the emergency-claim handler
    both check `is_paused` before acting on a paused participation."""
    await skip_today(session, khatm_id, participation_id)
    await participation_service.set_paused_until(session, participation_id, until)


async def resume_commitment(session: AsyncSession, participation_id) -> None:
    await participation_service.set_paused_until(session, participation_id, None)


async def cancel_khatm(
    session: AsyncSession, *, khatm_id, creator_user_id
) -> tuple[Khatm, int]:
    """Cancel an unused khatm and refund its recorded creation price internally."""
    khatm = await khatm_service.get_khatm(session, khatm_id)
    if khatm is None or khatm.creator_user_id != creator_user_id:
        raise KhatmCancellationError("khatm is not owned by the creator")
    if khatm.status != KhatmStatus.ACTIVE:
        raise KhatmCancellationError("only active khatms can be cancelled")
    if await participation_service.count_for_khatm(session, khatm_id) > 0:
        raise KhatmCancellationError("a member has already joined")

    amount = max(0, khatm.creation_price_toman)
    await khatm_service.cancel_khatm(session, khatm_id)
    if amount:
        invoiced_refund = await wallet_service.refund_purchase_invoice(
            session,
            user_id=creator_user_id,
            kind=InvoiceKind.KHATM_CREATION,
            resource_ref=str(khatm.id),
            description=f"بازپرداخت لغو ختم: {khatm.title}",
        )
        if invoiced_refund is not None:
            amount = invoiced_refund
        else:
            # Compatibility for khatms created before invoice migration.
            await wallet_service.refund_cash(
                session, creator_user_id, amount,
                description=f"بازپرداخت لغو ختم: {khatm.title}"
            )
    return khatm, amount


async def resolve_missed_commitment(
    session: AsyncSession, *, khatm_id, participation_id, decision: str
) -> tuple[Participation | None, KhatmPortion | None]:
    """Apply the creator's Q77 decision to a committed Quran participant.

    ``continue`` preserves the membership, ``open`` keeps the member active
    but removes their commitment/reminders, and ``replace`` leaves the member
    through the normal waiting-list promotion path.
    """
    if decision not in {"continue", "open", "replace"}:
        raise InvalidCreatorDecisionError("unknown creator decision")
    participation = await participation_service.get_by_id(session, participation_id)
    if participation is None or participation.khatm_id != khatm_id or not participation.is_committed:
        raise InvalidCreatorDecisionError("participation is not an active committed membership")
    khatm = await khatm_service.get_khatm(session, khatm_id)
    if khatm is None or khatm.template_type != KhatmTemplateType.QURAN_PAGE or khatm.khatm_type != KhatmTypeEnum.COMMITMENT:
        raise InvalidCreatorDecisionError("decision applies only to committed Quran khatms")

    resolution = {"continue": "CONTINUE", "open": "CONVERTED_OPEN", "replace": "REPLACED"}[decision]
    await participation_service.set_creator_resolution(session, participation_id, resolution)
    if decision == "continue":
        return None, None
    if decision == "open":
        current = await allocation_service.get_current_portion(session, khatm_id, participation_id)
        if current is not None:
            await allocation_service.release_portion(session, current.id)
        await participation_service.set_committed(session, participation_id, False)
        return None, None
    return await leave_khatm(session, participation_id, reason="creator_replace")
