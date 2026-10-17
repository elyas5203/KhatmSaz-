import pytest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from zoneinfo import ZoneInfo

from khatmsaz.modules.khatm.models import Khatm, KhatmStatus, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.khatm_category.models import KhatmCategory, KhatmCategoryGroup
from khatmsaz.modules.reporting.creator_daily_report import (
    deliver_creator_daily_reports,
    format_khatm_amount,
    format_persian_date,
    gregorian_to_jalali,
    to_persian_digits,
)


def test_persian_date_and_numbers_formatting():
    # Test Gregorian to Jalali
    jy, jm, jd = gregorian_to_jalali(2026, 10, 11)
    assert jy == 1405
    assert jm == 7
    assert jd == 19

    # Test formatted Persian string
    dt = datetime(2026, 10, 11, 12, 0, tzinfo=ZoneInfo("Asia/Tehran"))
    formatted = format_persian_date(dt)
    assert "یک‌شنبه" in formatted
    assert "مهر" in formatted
    assert "۱۴۰۵" in formatted

    # Test Persian digit converter
    assert to_persian_digits(12345) == "۱۲۳۴۵"
    assert to_persian_digits("0-9") == "۰-۹"


@pytest.mark.asyncio
async def test_format_khatm_amount_custom_units():
    session = AsyncMock()

    # 1. Salawat
    salawat_khatm = SimpleNamespace(
        id=uuid4(),
        template_type=KhatmTemplateType.SALAWAT,
        content_category_id=None,
        title="ختم صلوات",
    )
    with patch("khatmsaz.bot.member_copy.content_family", AsyncMock(return_value="salawat")):
        txt = await format_khatm_amount(session, salawat_khatm, 2500)
        assert txt == "۲،۵۰۰ صلوات"

    # 2. Khutbah Fadakiah (5 sections per round)
    fadak_khatm = SimpleNamespace(
        id=uuid4(),
        template_type=KhatmTemplateType.SALAWAT,
        content_category_id=uuid4(),
        title="ختم خطبه فدکیه",
    )
    with (
        patch("khatmsaz.bot.member_copy.content_family", AsyncMock(return_value="khutbah")),
        patch("khatmsaz.modules.khatm_category.service.get", AsyncMock(return_value=SimpleNamespace(devotional_slug="khutbah-fadakiah"))),
    ):
        txt = await format_khatm_amount(session, fadak_khatm, 7)
        assert "۱ دور" in txt
        assert "۲ بخش" in txt

    # 3. Khutbah Ghadir (8 sections per round)
    ghadir_khatm = SimpleNamespace(
        id=uuid4(),
        template_type=KhatmTemplateType.SALAWAT,
        content_category_id=uuid4(),
        title="ختم خطبه غدیر",
    )
    with (
        patch("khatmsaz.bot.member_copy.content_family", AsyncMock(return_value="khutbah")),
        patch("khatmsaz.modules.khatm_category.service.get", AsyncMock(return_value=SimpleNamespace(devotional_slug="khutbah-ghadir"))),
    ):
        txt = await format_khatm_amount(session, ghadir_khatm, 11)
        assert "۱ دور" in txt
        assert "۳ بخش" in txt

    # 4. Quran open pages (604 pages per round)
    quran_khatm = SimpleNamespace(
        id=uuid4(),
        template_type=KhatmTemplateType.QURAN_PAGE,
        content_category_id=None,
        title="ختم قرآن کریم",
    )
    with patch("khatmsaz.bot.member_copy.content_family", AsyncMock(return_value="quran")):
        txt = await format_khatm_amount(session, quran_khatm, 606)
        assert "۱ دور ختم کامل" in txt
        assert "۲ صفحه" in txt


@pytest.mark.asyncio
async def test_canonical_seed_contains_khutbah_ghadir():
    from khatmsaz.modules.khatm_category import service as category_service

    added_objects = []
    session = AsyncMock()
    session.add = lambda obj: added_objects.append(obj)
    session.scalar = AsyncMock(return_value=None)

    seeded = await category_service.seed_canonical_categories(session)
    assert len(seeded) == 2
    assert "khutbah_ghadir" in seeded
    ghadir_cats = [
        c for c in added_objects
        if getattr(c, "devotional_slug", None) == "khutbah-ghadir"
    ]
    assert len(ghadir_cats) == 1
    cat = ghadir_cats[0]
    assert cat.group == KhatmCategoryGroup.KHUTBAH
    assert "غدیر" in cat.title


@pytest.mark.asyncio
async def test_multimedia_trio_registration_and_retrieval():
    from khatmsaz.modules.content import service as content_service
    from khatmsaz.modules.content.models import DevotionalAsset, DevotionalMedia

    asset_id = uuid4()
    asset = DevotionalAsset(
        id=asset_id,
        content_type="DUA",
        slug="khutbah-ghadir",
        title="خطبه غدیر پیامبر اکرم (ص)",
        text_body="",
        enabled=True,
    )

    media_store: list[DevotionalMedia] = []

    session = AsyncMock()

    async def fake_scalar(stmt):
        stmt_str = str(stmt)
        if "devotional_assets" in stmt_str:
            return asset
        return None

    async def fake_execute(stmt):
        result = AsyncMock()
        filtered = [
            m for m in media_store
            if m.page_number == 1 and m.asset_platform == "TELEGRAM"
        ]
        mock_scalars = AsyncMock()
        mock_scalars.all = lambda: filtered
        result.scalars = lambda: mock_scalars
        return result

    def fake_add(obj):
        media_store.append(obj)

    session.scalar = AsyncMock(side_effect=fake_scalar)
    session.execute = AsyncMock(side_effect=fake_execute)
    session.add = fake_add

    # Register Trio for part 1
    vid = await content_service.add_devotional_video_page(
        session, slug="khutbah-ghadir", asset_ref="vid_part_1", asset_platform="TELEGRAM", page_number=1, caption="ویدیو ۱"
    )
    pdf = await content_service.add_devotional_pdf_page(
        session, slug="khutbah-ghadir", asset_ref="pdf_part_1", asset_platform="TELEGRAM", page_number=1, caption="پی‌دی‌اف ۱"
    )
    aud = await content_service.add_devotional_audio_page(
        session, slug="khutbah-ghadir", asset_ref="aud_part_1", asset_platform="TELEGRAM", page_number=1, caption="صوت ۱"
    )

    assert vid.kind == "VIDEO" and vid.page_number == 1
    assert pdf.kind == "PDF" and pdf.page_number == 1
    assert aud.kind == "AUDIO" and aud.page_number == 1

    trio = await content_service.list_devotional_media_for_part(
        session, slug="khutbah-ghadir", page_number=1, asset_platform="TELEGRAM"
    )
    kinds = {m.kind for m in trio}
    assert kinds == {"VIDEO", "PDF", "AUDIO"}


@pytest.mark.asyncio
async def test_creator_daily_report_delivery_at_noon():
    creator_id = uuid4()
    khatm_id = uuid4()

    khatm = SimpleNamespace(
        id=khatm_id,
        creator_user_id=creator_id,
        title="ختم صلوات برای فرج",
        status=KhatmStatus.ACTIVE,
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
        content_category_id=None,
        repetition_target=14000,
        created_at=datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc),
    )

    settings = SimpleNamespace(
        user_id=creator_id,
        timezone="Asia/Tehran",
        creator_daily_report_enabled=True,
        last_creator_daily_report_date=None,
    )

    user = SimpleNamespace(
        id=creator_id,
        status=SimpleNamespace(value="ACTIVE"),
        deleted_at=None,
    )

    identity = SimpleNamespace(
        platform=SimpleNamespace(value="TELEGRAM"),
        subject="12345678",
    )

    session = AsyncMock()

    # Mock DB execution
    async def fake_execute(stmt):
        mock_res = AsyncMock()
        stmt_str = str(stmt).lower()
        if "distinct" in stmt_str and "creator_user_id" in stmt_str:
            mock_res.scalars = lambda: [creator_id]
        elif "from khatms" in stmt_str:
            mock_res.scalars = lambda: [khatm]
        return mock_res

    session.execute = AsyncMock(side_effect=fake_execute)

    # 1. Before 12:00 PM (e.g. 11:30 Tehran time)
    before_noon = datetime(2026, 10, 11, 8, 0, tzinfo=timezone.utc)  # 11:30 in Asia/Tehran (+03:30)
    delivered = await deliver_creator_daily_reports(
        session, AsyncMock(), tz_name="Asia/Tehran", now=before_noon, creator_user_ids={creator_id}
    )
    assert delivered == 0
    assert settings.last_creator_daily_report_date is None

    # 2. At 12:05 PM Tehran time
    at_noon = datetime(2026, 10, 11, 8, 35, tzinfo=timezone.utc)  # 12:05 in Asia/Tehran (+03:30)

    delivered_messages = []
    async def fake_send_keyboard(platform, chat_id, text, keyboard):
        delivered_messages.append((text, keyboard))
        return True

    with (
        patch("khatmsaz.modules.settings.service.get_or_create", AsyncMock(return_value=settings)),
        patch("khatmsaz.modules.identity.service.find_by_id", AsyncMock(return_value=user)),
        patch("khatmsaz.modules.identity.service.list_identities_for_user", AsyncMock(return_value=[identity])),
        patch("khatmsaz.modules.reporting.creator_daily_report.get_khatm_daily_counts", AsyncMock(return_value=(1000.0, 500.0, 1500.0, 12))),
        patch("khatmsaz.modules.reporting.creator_daily_report.send_with_keyboard", side_effect=fake_send_keyboard),
        patch("khatmsaz.bot.member_copy.content_family", AsyncMock(return_value="salawat")),
    ):
        delivered = await deliver_creator_daily_reports(
            session, AsyncMock(), tz_name="Asia/Tehran", now=at_noon, creator_user_ids={creator_id}
        )
        assert delivered == 1
        assert settings.last_creator_daily_report_date == "2026-10-11"
        assert len(delivered_messages) == 1

        text, keyboard = delivered_messages[0]
        assert "گزارش روزانه ختم‌های شما (ساعت ۱۲:۰۰ ظهر)" in text
        assert "پیشرفت تا دیروز: ۱،۰۰۰ صلوات" in text
        assert "قرائت‌های امروز (تا ساعت ۱۲): ۵۰۰ صلوات" in text
        assert "مجموع قرائت‌شده: <b>۱،۵۰۰ صلوات</b>" in text
        assert "همراهان فعال: ۱۲ نفر" in text
        assert "طاعت و خدمت خالصانه‌تان قبول درگاه حق" in text

        # 3. Call again on the same day -> Must be idempotent and return 0
        delivered_again = await deliver_creator_daily_reports(
            session, AsyncMock(), tz_name="Asia/Tehran", now=at_noon, creator_user_ids={creator_id}
        )
        assert delivered_again == 0
