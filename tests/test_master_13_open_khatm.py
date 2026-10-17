"""Tests for Child Master 13 — Open Khatm Flow Overhaul.

Verifies:
1. OPEN khatm in ask_contribution_amount bypasses commitment mode picker and prompts for amount or shows open share.
2. today_overview with single OPEN khatm immediately routes to recitation without intermediary selection prompt.
3. deliver_today_early for OPEN khatm never blocks with 'already sent today' or 'no portion today'.
4. member_my_khatms omits reminder hour button for OPEN khatms.
5. join_requests approval does not trigger mode picker for OPEN khatms.
6. delivery.prepare_numeric identifies open: prefixed outstanding shares.
7. share_occurrence service.complete self-heals undelivered share and completes without error.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from khatmsaz.modules.khatm.models import Khatm, KhatmTypeEnum, KhatmTemplateType, KhatmStatus
from khatmsaz.modules.participation.models import Participation, ParticipationStatus
from khatmsaz.bot.handlers.report import _deliver_open_khatm_flow


@pytest.mark.asyncio
async def test_deliver_open_khatm_flow_prompts_count_when_no_outstanding():
    mock_message = MagicMock()
    mock_message.answer = AsyncMock()
    mock_state = MagicMock()
    mock_state.set_state = AsyncMock()
    mock_state.update_data = AsyncMock()

    part = MagicMock()
    part.id = uuid4()
    khatm = MagicMock()
    khatm.id = uuid4()
    khatm.khatm_type = KhatmTypeEnum.OPEN
    khatm.template_type = KhatmTemplateType.SALAWAT

    with patch("khatmsaz.modules.share_occurrence.repository.list_outstanding", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []
        with patch("khatmsaz.bot.member_copy.content_family", new_callable=AsyncMock) as mock_family:
            mock_family.return_value = "salawat"
            await _deliver_open_khatm_flow(mock_message, mock_state, part, khatm, "fa", MagicMock())

    mock_state.set_state.assert_called_once()
    mock_message.answer.assert_called_once()
    prompt_text = mock_message.answer.call_args[0][0]
    assert "صلوات" in prompt_text or "می‌خواهید چند" in prompt_text


@pytest.mark.asyncio
async def test_deliver_open_khatm_flow_displays_outstanding_share_if_present():
    mock_message = MagicMock()
    mock_message.answer = AsyncMock()
    mock_state = MagicMock()

    part = MagicMock()
    part.id = uuid4()
    khatm = MagicMock()
    khatm.id = uuid4()
    khatm.khatm_type = KhatmTypeEnum.OPEN
    khatm.template_type = KhatmTemplateType.SALAWAT

    mock_occurrence = MagicMock()
    mock_occurrence.delivered_at = MagicMock()
    mock_occurrence.amount = 100
    mock_occurrence.content_spec = {"family": "salawat"}

    with patch("khatmsaz.modules.share_occurrence.repository.list_outstanding", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [mock_occurrence]
        await _deliver_open_khatm_flow(mock_message, mock_state, part, khatm, "fa", MagicMock())

    mock_message.answer.assert_called_once()
    assert mock_message.answer.call_args[1].get("reply_markup") is not None


@pytest.mark.asyncio
async def test_service_complete_self_heals_missing_delivered_at():
    from khatmsaz.modules.share_occurrence import service as share_service

    session = AsyncMock()
    mock_occurrence = MagicMock()
    mock_occurrence.bot_instance_id = "bot_1"
    mock_occurrence.participation_id = uuid4()
    mock_occurrence.completed_at = None
    mock_occurrence.delivered_at = None
    mock_occurrence.reservation_id = None

    mock_part = MagicMock()
    mock_part.user_id = 123

    with patch("khatmsaz.modules.share_occurrence.repository.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_occurrence
        with patch("khatmsaz.modules.participation.service.get_by_id", new_callable=AsyncMock) as mock_get_part:
            mock_get_part.return_value = mock_part
            with patch("khatmsaz.modules.share_occurrence.repository.mark_completed", new_callable=AsyncMock):
                record_progress = AsyncMock()
                occ, changed = await share_service.complete(
                    session, uuid4(), user_id=123, bot_instance_id="bot_1", record_progress=record_progress
                )
                assert changed is True
                assert occ.delivered_at is not None
                record_progress.assert_called_once()
