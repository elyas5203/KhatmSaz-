import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.content.models import QuranAssetKind, QuranPageAsset


@pytest.mark.integration
@pytest.mark.asyncio
async def test_channel_range_registry_is_idempotent_and_resolves_shared_audio():
    async with session_scope() as session:
        first = await content_service.register_telegram_channel_asset_range(
            session, source_chat_id=-1001127138974, source_message_id=12,
            page_start=1, page_end=3, kind=QuranAssetKind.AUDIO,
        )
        second = await content_service.register_telegram_channel_asset_range(
            session, source_chat_id=-1001127138974, source_message_id=999,
            page_start=1, page_end=3, kind=QuranAssetKind.AUDIO,
        )
        assert [row.id for row in first] == [row.id for row in second]
        rows = await content_service.resolve_complete_quran_page_assets(
            session, edition_id="madina-hafs", page_start=1, page_end=3,
            kind=QuranAssetKind.AUDIO, reciter_id="parhizgar",
        )
        assert len(rows) == 3
        assert {row.asset_ref for row in rows} == {
            content_service.encode_telegram_forward_ref(-1001127138974, 999)
        }
        await session.execute(delete(QuranPageAsset))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_channel_coverage_counts_pages_not_source_posts():
    async with session_scope() as session:
        await content_service.register_telegram_channel_asset_range(
            session, source_chat_id=-1001127138974, source_message_id=10,
            page_start=1, page_end=2, kind=QuranAssetKind.IMAGE,
        )
        coverage = await content_service.quran_channel_coverage(session)
        assert coverage["image_count"] == 2
        assert coverage["audio_count"] == 0
        assert coverage["ready"] is False
        assert coverage["missing_images"][:2] == [3, 4]
        await session.execute(delete(QuranPageAsset))
