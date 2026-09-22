import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.content.models import QuranAssetKind, QuranPageAsset


@pytest.mark.integration
@pytest.mark.asyncio
async def test_quran_page_assets_require_canonical_complete_ranges():
    async with session_scope() as session:
        await content_service.register_quran_page_asset(
            session, edition_id="madina-hafs", page_number=10,
            kind=QuranAssetKind.IMAGE, asset_ref="quran/page-010.webp",
        )
        await content_service.register_quran_page_asset(
            session, edition_id="madina-hafs", page_number=10,
            kind=QuranAssetKind.IMAGE, asset_ref="bale-file-id-010",
            asset_platform="BALE",
        )
        await content_service.register_quran_page_asset(
            session, edition_id="madina-hafs", page_number=12,
            kind=QuranAssetKind.IMAGE, asset_ref="quran/page-012.webp",
        )
        assert await content_service.resolve_complete_quran_page_assets(
            session, edition_id="madina-hafs", page_start=10, page_end=12,
            kind=QuranAssetKind.IMAGE,
        ) is None

        await content_service.register_quran_page_asset(
            session, edition_id="madina-hafs", page_number=11,
            kind=QuranAssetKind.IMAGE, asset_ref="quran/page-011.webp",
        )
        rows = await content_service.resolve_complete_quran_page_assets(
            session, edition_id="madina-hafs", page_start=10, page_end=12,
            kind=QuranAssetKind.IMAGE,
        )
        assert [row.page_number for row in rows] == [10, 11, 12]
        bale_rows = await content_service.resolve_complete_quran_page_assets(
            session, edition_id="madina-hafs", page_start=10, page_end=10,
            kind=QuranAssetKind.IMAGE, asset_platform="BALE",
        )
        assert [row.asset_ref for row in bale_rows] == ["bale-file-id-010"]

        with pytest.raises(ValueError):
            await content_service.register_quran_page_asset(
                session, edition_id="other", page_number=10,
                kind=QuranAssetKind.IMAGE, asset_ref="other/page.webp",
            )
        with pytest.raises(ValueError):
            await content_service.register_quran_page_asset(
                session, edition_id="madina-hafs", page_number=605,
                kind=QuranAssetKind.IMAGE, asset_ref="quran/page-605.webp",
            )

        await session.execute(delete(QuranPageAsset))
