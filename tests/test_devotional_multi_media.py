"""Owner request (2026-09-22): a devotional asset (dua/ziyarat) can now
have more than one reciter's audio, more than one image page (a long dua
spanning several photos), and a PDF — the old single audio_ref/image_ref
columns only ever held one of each. See
`content/service.py::add_devotional_audio_variant`,
`add_devotional_image_page`, `set_devotional_pdf`."""

import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.content.models import DevotionalAsset, DevotionalMedia


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_reciters_multiple_pages_and_pdf():
    slug = f"test-multi-{new_id()}"[:40]
    async with session_scope() as session:
        await content_service.register_devotional_text(
            session, content_type="DUA", slug=slug, title="تست چندرسانه‌ای", text_body="متن آزمایشی",
        )

        # Two different reciters for the same dua.
        await content_service.add_devotional_audio_variant(
            session, slug=slug, asset_ref="AUDIO_REF_1", asset_platform="TELEGRAM",
            reciter_id="parhizgar", reciter_label="پرهیزگار",
        )
        await content_service.add_devotional_audio_variant(
            session, slug=slug, asset_ref="AUDIO_REF_2", asset_platform="TELEGRAM",
            reciter_id="mahmoudi", reciter_label="محمودی",
        )
        variants = await content_service.list_devotional_audio_variants(session, slug, "TELEGRAM")
        assert {v.reciter_id for v in variants} == {"parhizgar", "mahmoudi"}
        assert {v.asset_ref for v in variants} == {"AUDIO_REF_1", "AUDIO_REF_2"}

        # Re-uploading the same reciter updates in place, doesn't duplicate.
        await content_service.add_devotional_audio_variant(
            session, slug=slug, asset_ref="AUDIO_REF_1_UPDATED", asset_platform="TELEGRAM",
            reciter_id="parhizgar", reciter_label="پرهیزگار",
        )
        variants = await content_service.list_devotional_audio_variants(session, slug, "TELEGRAM")
        assert len(variants) == 2
        assert any(v.asset_ref == "AUDIO_REF_1_UPDATED" for v in variants)

        # Multiple image pages, auto-appending page numbers.
        p1 = await content_service.add_devotional_image_page(session, slug=slug, asset_ref="IMG_1", asset_platform="TELEGRAM")
        p2 = await content_service.add_devotional_image_page(session, slug=slug, asset_ref="IMG_2", asset_platform="TELEGRAM")
        assert p1.page_number == 1
        assert p2.page_number == 2
        pages = await content_service.list_devotional_image_pages(session, slug, "TELEGRAM")
        assert [p.asset_ref for p in pages] == ["IMG_1", "IMG_2"]

        # Explicit page number insert/update.
        await content_service.add_devotional_image_page(
            session, slug=slug, asset_ref="IMG_1_FIXED", asset_platform="TELEGRAM", page_number=1,
        )
        pages = await content_service.list_devotional_image_pages(session, slug, "TELEGRAM")
        assert pages[0].asset_ref == "IMG_1_FIXED"
        assert len(pages) == 2

        # PDF single slot.
        await content_service.set_devotional_pdf(session, slug=slug, asset_ref="PDF_1", asset_platform="TELEGRAM")
        pdf = await content_service.get_devotional_pdf(session, slug, "TELEGRAM")
        assert pdf.asset_ref == "PDF_1"
        await content_service.set_devotional_pdf(session, slug=slug, asset_ref="PDF_2", asset_platform="TELEGRAM")
        pdf = await content_service.get_devotional_pdf(session, slug, "TELEGRAM")
        assert pdf.asset_ref == "PDF_2"

        asset = await content_service.get_devotional_asset(session, slug)
        await session.execute(delete(DevotionalMedia).where(DevotionalMedia.devotional_asset_id == asset.id))
        await session.execute(delete(DevotionalAsset).where(DevotionalAsset.id == asset.id))
