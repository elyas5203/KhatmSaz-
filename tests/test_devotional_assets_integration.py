import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.content.models import DevotionalAsset


@pytest.mark.integration
@pytest.mark.asyncio
async def test_devotional_text_and_platform_specific_audio():
    async with session_scope() as session:
        asset = await content_service.register_devotional_text(
            session, content_type="dua", slug="dua-test", title="دعای تست",
            text_body="متن کامل دعای آزمایشی",
        )
        await content_service.register_devotional_audio(
            session, slug="dua-test", asset_ref="telegram-audio", asset_platform="telegram",
        )
        loaded = await content_service.get_devotional_asset(session, "DUA-TEST")
        assert loaded.id == asset.id
        assert loaded.content_type == "DUA"
        assert loaded.text_body == "متن کامل دعای آزمایشی"
        assert loaded.audio_ref == "telegram-audio"
        assert loaded.audio_platform == "TELEGRAM"

        with pytest.raises(ValueError):
            await content_service.register_devotional_text(
                session, content_type="CUSTOM", slug="bad", title="بد", text_body="متن"
            )
        await session.execute(delete(DevotionalAsset).where(DevotionalAsset.id == asset.id))
