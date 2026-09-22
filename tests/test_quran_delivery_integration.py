import pytest
from sqlalchemy import delete

from khatmsaz.core.db import session_scope
from khatmsaz.core.ids import new_id
from khatmsaz.modules.content import service as content_service
from khatmsaz.modules.content.models import KhatmReciter, QuranAssetKind, QuranPageAsset
from khatmsaz.modules.identity.models import User
from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.settings.models import UserSettings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_current_quran_delivery_is_exact_and_reciter_specific():
    user_id, khatm_id = new_id(), new_id()
    async with session_scope() as session:
        session.add(User(id=user_id, display_name="delivery-test"))
        session.add(UserSettings(user_id=user_id, preferred_reciter="husary", quran_audio_enabled=True))
        khatm = Khatm(
            id=khatm_id, creator_user_id=user_id, title="تحویل تستی",
            template_type=KhatmTemplateType.QURAN_PAGE, khatm_type=KhatmTypeEnum.COMMITMENT,
            quran_edition_id="madina-hafs", status=KhatmStatus.ACTIVE,
        )
        session.add(khatm)
        await session.flush()
        await content_service.set_allowed_reciters(session, khatm_id, ["husary"])
        for page in (10, 11):
            await content_service.register_quran_page_asset(
                session, edition_id="madina-hafs", page_number=page,
                kind=QuranAssetKind.IMAGE, asset_ref=f"img-{page}",
            )
            await content_service.register_quran_page_asset(
                session, edition_id="madina-hafs", page_number=page,
                kind=QuranAssetKind.AUDIO, reciter_id="husary", asset_ref=f"audio-{page}",
            )
            await content_service.register_quran_page_asset(
                session, edition_id="madina-hafs", page_number=page,
                kind=QuranAssetKind.TEXT, asset_ref=f"text-{page}",
            )
        delivery = await content_service.resolve_current_quran_delivery(
            session, khatm=khatm, user_id=user_id, page_start=10, page_end=11,
        )
        assert [asset.asset_ref for asset in delivery["image"]] == ["img-10", "img-11"]
        assert [asset.asset_ref for asset in delivery["audio"]] == ["audio-10", "audio-11"]
        assert delivery["reciter_id"] == "husary"
        assert delivery["text"] is None
        await content_service.set_content_delivery_mode(
            session, khatm_id=khatm_id, creator_user_id=user_id, mode="text",
        )
        settings = await session.get(UserSettings, user_id)
        settings.translation_enabled = True
        text_delivery = await content_service.resolve_current_quran_delivery(
            session, khatm=khatm, user_id=user_id, page_start=10, page_end=11,
        )
        assert text_delivery["image"] is None
        assert [asset.asset_ref for asset in text_delivery["text"]] == ["text-10", "text-11"]
        await session.execute(delete(QuranPageAsset))
        await session.execute(delete(KhatmReciter).where(KhatmReciter.khatm_id == khatm_id))
        await session.execute(delete(UserSettings).where(UserSettings.user_id == user_id))
        await session.execute(delete(Khatm).where(Khatm.id == khatm_id))
        await session.execute(delete(User).where(User.id == user_id))
