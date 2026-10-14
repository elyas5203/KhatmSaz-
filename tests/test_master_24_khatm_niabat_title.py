import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from khatmsaz.modules.khatm.models import Khatm, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.bot.member_copy import (
    extract_proxy_name,
    get_khatm_display_title,
    format_khatm_report_header,
)
from khatmsaz.modules.reporting.creator_daily_report import build_creator_daily_report_message
from khatmsaz.modules.reporting.member_daily_digest import build_member_daily_digest_message


def test_extract_proxy_name():
    # Persian standard suffix
    n1 = "به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف — به نیابت از مرحوم مغفور مهندس علی اکبر مویدی"
    assert extract_proxy_name(n1) == "مرحوم مغفور مهندس علی اکبر مویدی"

    n2 = "به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف — به نیابت از مرحومه زهرا حامد مقدم"
    assert extract_proxy_name(n2) == "مرحومه زهرا حامد مقدم"

    n3 = "به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف — به نیابت از پدرم اقای بهمن ابادی"
    assert extract_proxy_name(n3) == "پدرم اقای بهمن ابادی"

    # Direct prefixes
    assert extract_proxy_name("به نیابت از برادرم شهید محمد") == "برادرم شهید محمد"
    assert extract_proxy_name("نیابت از رفتگانم") == "رفتگانم"

    # Arabic
    assert extract_proxy_name("بنية ظهور الإمام المهدي — نيابةً عن والدي المرحوم") == "والدي المرحوم"

    # English
    assert extract_proxy_name("For the reappearance — on behalf of John Doe") == "John Doe"

    # No proxy
    assert extract_proxy_name("به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف") is None
    assert extract_proxy_name("") is None
    assert extract_proxy_name(None) is None


def test_get_khatm_display_title():
    # 1. Generic title "ختم قرآن" with proxy
    k1 = Khatm(
        title="ختم قرآن",
        niyyat="به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف — به نیابت از مرحوم مغفور مهندس علی اکبر مویدی",
        template_type=KhatmTemplateType.QURAN_PAGE,
        khatm_type=KhatmTypeEnum.COMMITMENT,
    )
    assert get_khatm_display_title(k1, "fa") == "به نیابت از مرحوم مغفور مهندس علی اکبر مویدی"

    # 2. Specific custom title without proxy
    k2 = Khatm(
        title="تست ختم قرآن اوووو",
        niyyat="به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف",
        template_type=KhatmTemplateType.QURAN_PAGE,
        khatm_type=KhatmTypeEnum.COMMITMENT,
    )
    assert get_khatm_display_title(k2, "fa") == "تست ختم قرآن اوووو"

    # 3. Already has "به نیابت از" title
    k3 = Khatm(
        title="به نیابت از مرحومه زهرا حامد مقدم",
        niyyat="به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف — به نیابت از مرحومه زهرا حامد مقدم",
        template_type=KhatmTemplateType.QURAN_PAGE,
        khatm_type=KhatmTypeEnum.COMMITMENT,
    )
    assert get_khatm_display_title(k3, "fa") == "به نیابت از مرحومه زهرا حامد مقدم"

    # 4. Generic title with no proxy
    k4 = Khatm(
        title="ختم قرآن",
        niyyat="به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف",
        template_type=KhatmTemplateType.QURAN_PAGE,
        khatm_type=KhatmTypeEnum.COMMITMENT,
    )
    assert get_khatm_display_title(k4, "fa") == "ختم قرآن"


@pytest.mark.asyncio
async def test_format_khatm_report_header():
    mock_session = AsyncMock()

    # 1. Quran with proxy
    k1 = Khatm(
        title="ختم قرآن",
        niyyat="به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف — به نیابت از مرحوم مغفور مهندس علی اکبر مویدی",
        template_type=KhatmTemplateType.QURAN_PAGE,
        khatm_type=KhatmTypeEnum.COMMITMENT,
    )
    h1 = await format_khatm_report_header(mock_session, k1, "fa")
    assert h1 == "🌟 <b>به نیابت از مرحوم مغفور مهندس علی اکبر مویدی</b> (ختم قرآن)"

    # 2. Salawat with title already "ختم صلوات" and no proxy: NO duplicate "ختم «ختم صلوات»"
    k2 = Khatm(
        title="ختم صلوات",
        niyyat="به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
    )
    h2 = await format_khatm_report_header(mock_session, k2, "fa")
    assert h2 == "🌟 <b>ختم صلوات</b>"
    assert "ختم «ختم" not in h2

    # 3. Ziyarat with title "ختم زیارت آل یاسین": NO duplicate "ختم «ختم ...»"
    k3 = Khatm(
        title="ختم زیارت آل یاسین",
        niyyat="به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
    )
    h3 = await format_khatm_report_header(mock_session, k3, "fa")
    assert h3 == "🌟 <b>ختم زیارت آل یاسین</b>"
    assert "ختم «ختم" not in h3

    # 4. Custom title like "تست ختم قرآن اوووو"
    k4 = Khatm(
        title="تست ختم قرآن اوووو",
        niyyat="به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف",
        template_type=KhatmTemplateType.QURAN_PAGE,
        khatm_type=KhatmTypeEnum.COMMITMENT,
    )
    h4 = await format_khatm_report_header(mock_session, k4, "fa")
    assert h4 == "🌟 <b>ختم «تست ختم قرآن اوووو»</b>"


@pytest.mark.asyncio
async def test_creator_daily_report_renders_niabat():
    mock_session = AsyncMock()

    khatm = Khatm(
        id="khatm-123",
        title="ختم قرآن",
        niyyat="به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف — به نیابت از مرحوم مغفور مهندس علی اکبر مویدی",
        template_type=KhatmTemplateType.QURAN_PAGE,
        khatm_type=KhatmTypeEnum.COMMITMENT,
    )

    now_utc = datetime(2026, 10, 14, 8, 30, tzinfo=timezone.utc)
    today_start_utc = datetime(2026, 10, 14, 0, 0, tzinfo=timezone.utc)
    local_now = now_utc

    body, kb = await build_creator_daily_report_message(
        mock_session,
        [khatm],
        local_now=local_now,
        today_start_utc=today_start_utc,
        now_utc=now_utc,
    )

    # Verify headline uses Niabat and devotional
    assert "🌟 <b>به نیابت از مرحوم مغفور مهندس علی اکبر مویدی</b> (ختم قرآن)" in body
    assert "ختم «ختم قرآن»" not in body


@pytest.mark.asyncio
async def test_member_daily_digest_renders_niabat():
    mock_session = AsyncMock()
    mock_session.scalar = AsyncMock(return_value=0)

    khatm = Khatm(
        id="khatm-456",
        title="ختم قرآن",
        niyyat="به نیت ظهور امام زمان عجل الله تعالی فرجه الشریف — به نیابت از مرحومه زهرا حامد مقدم",
        template_type=KhatmTemplateType.QURAN_PAGE,
        khatm_type=KhatmTypeEnum.COMMITMENT,
    )
    participation = MagicMock()
    participation.id = "part-1"

    now_utc = datetime(2026, 10, 14, 10, 30, tzinfo=timezone.utc)
    today_start_utc = datetime(2026, 10, 14, 0, 0, tzinfo=timezone.utc)
    local_now = now_utc

    body, _ = await build_member_daily_digest_message(
        mock_session,
        [(khatm, participation)],
        local_now=local_now,
        today_start_utc=today_start_utc,
        now_utc=now_utc,
    )

    # Verify headline uses Niabat
    assert "🌟 <b>به نیابت از مرحومه زهرا حامد مقدم</b> (ختم قرآن)" in body
    assert "ختم «ختم قرآن»" not in body


@pytest.mark.asyncio
async def test_wizard_enter_niyyat_syncs_title():
    from khatmsaz.bot.handlers.create_khatm import enter_niyyat, skip_niyyat
    state_data = {
        "template_type": KhatmTemplateType.QURAN_PAGE.value,
        "title": "ختم قرآن",
    }

    mock_state = AsyncMock()
    mock_state.get_data.return_value = state_data

    async def update_data(**kwargs):
        state_data.update(kwargs)
    mock_state.update_data.side_effect = update_data

    # 1. Message with proxy
    msg = MagicMock()
    msg.text = "به نیابت از مرحوم مغفور مهندس علی اکبر مویدی"
    msg.bot = MagicMock()
    msg.answer = AsyncMock()
    msg.from_user = MagicMock()
    msg.from_user.is_bot = False

    await enter_niyyat(msg, mock_state)

    assert state_data["title"] == "به نیابت از مرحوم مغفور مهندس علی اکبر مویدی"
    assert "به نیابت از مرحوم مغفور مهندس علی اکبر مویدی" in state_data["niyyat"]

    # 2. Skip niyyat restores default title
    cb = MagicMock()
    cb.message = MagicMock()
    cb.message.bot = MagicMock()
    cb.message.answer = AsyncMock()
    cb.from_user = MagicMock()
    cb.from_user.is_bot = False

    await skip_niyyat(cb, mock_state)

    assert state_data["title"] == "ختم قرآن"
    assert "مرحوم" not in state_data["niyyat"]

