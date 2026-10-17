import pytest
from types import SimpleNamespace
from uuid import uuid4

from khatmsaz.bot.handlers.start import build_join_preview_message
from khatmsaz.bot.member_copy import completion_text
from khatmsaz.i18n import t
from khatmsaz.modules.khatm.models import Khatm, KhatmTemplateType, KhatmTypeEnum
from khatmsaz.modules.bot_registry.models import BotCategory


def test_khutbah_join_preview_message():
    khatm = Khatm(
        id=uuid4(),
        title="ختم خطبه فدکیه",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
        niyyat="فرج امام زمان عجل الله تعالی فرجه الشریف",
        welcome_text="خوش آمدید",
    )
    preview = build_join_preview_message(
        khatm,
        creator_name="خادم",
        member_count=5,
        lang="fa",
        category_title="خطبه فدکیه حضرت فاطمه زهرا (س)",
        category_group="KHUTBAH",
    )
    assert "📜" in preview
    assert "خطبه" in preview
    assert "خطبه فدکیه حضرت فاطمه زهرا (س)" in preview


def test_khutbah_completion_verb():
    khatm = SimpleNamespace(
        title="ختم خطبه فدکیه",
        niyyat="سلامتی و فرج امام عصر علیه السلام",
    )
    msg = completion_text(khatm, "khutbah", "بخش ۱ از خطبه فدکیه", lang="fa")
    assert "✅ بخش ۱ از خطبه فدکیه قرائت شد." in msg
    assert "انجام شد" not in msg


def test_bot_category_enum_includes_khutbah():
    assert hasattr(BotCategory, "KHUTBAH")
    assert BotCategory.KHUTBAH.value == "KHUTBAH"


def test_khutbah_routing_to_dua_ziyarat_bot():
    from khatmsaz.bot.handlers.create_khatm import _bot_category_for
    from khatmsaz.modules.bot_registry import service as bot_reg_service
    from khatmsaz.modules.khatm_category.models import KhatmCategory, KhatmCategoryGroup

    # 1. Wizard category resolution
    wizard_cat = _bot_category_for(KhatmTemplateType.SALAWAT.value, KhatmCategoryGroup.KHUTBAH.value)
    assert wizard_cat == BotCategory.DUA_ZIYARAT.value

    # 2. Service resolution for Khatm
    khatm = Khatm(
        id=uuid4(),
        title="ختم خطبه فدکیه",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.OPEN,
    )
    cat = KhatmCategory(
        id=uuid4(),
        group=KhatmCategoryGroup.KHUTBAH,
        title="خطبه فدکیه",
    )
    resolved = bot_reg_service.resolve_bot_category(khatm, cat)
    assert resolved == BotCategory.DUA_ZIYARAT


@pytest.mark.asyncio
async def test_add_devotional_video_page_autoprovisions_asset():
    from khatmsaz.modules.content import service as content_service
    added = []

    class MockSession:
        async def scalar(self, stmt):
            return None

        def add(self, entity):
            added.append(entity)

        async def flush(self):
            pass

    session = MockSession()
    media = await content_service.add_devotional_video_page(
        session, slug="khutbah-fadakiah", asset_ref="video-ref-1", asset_platform="TELEGRAM", page_number=1,
    )
    assert media.page_number == 1
    assert media.asset_ref == "video-ref-1"
    # Auto-created devotional asset with DUA type for Postgres check constraint compatibility
    created_asset = next((e for e in added if getattr(e, "slug", None) == "khutbah-fadakiah"), None)
    assert created_asset is not None
    assert created_asset.content_type == "DUA"


def test_decode_telegram_forward_ref_supports_tg_forward_and_usernames():
    from khatmsaz.modules.content.service import decode_telegram_forward_ref

    res1 = decode_telegram_forward_ref("tg_forward:@khedmatgozaran_group:25286")
    assert res1 == ("@khedmatgozaran_group", 25286)

    res2 = decode_telegram_forward_ref("telegram-forward:-10012345:99")
    assert res2 == (-10012345, 99)

    res3 = decode_telegram_forward_ref("invalid_ref")
    assert res3 is None


@pytest.mark.asyncio
async def test_seed_canonical_categories_creates_khutbah_category():
    from khatmsaz.modules.khatm_category import service as category_service
    from khatmsaz.modules.khatm_category.models import KhatmCategoryGroup
    added = []

    class MockSession:
        async def scalar(self, stmt):
            return None

        def add(self, entity):
            added.append(entity)

        async def flush(self):
            pass

    session = MockSession()
    result = await category_service.seed_canonical_categories(session)
    assert "khutbah_fadakiah" in result
    cat = next((e for e in added if getattr(e, "devotional_slug", None) == "khutbah-fadakiah"), None)
    assert cat is not None
    assert cat.group == KhatmCategoryGroup.KHUTBAH
    assert cat.title == "خطبه فدکیه حضرت فاطمه زهرا (س)"


def test_calc_deadline_supports_end_of_day_24():
    from datetime import datetime, timezone
    from khatmsaz.modules.share_occurrence.delivery import _calc_deadline

    local = datetime(2026, 10, 8, 14, 30, tzinfo=timezone.utc)
    # Hour 24 should be 00:00:00 of next day
    deadline_24 = _calc_deadline(local, 24)
    assert deadline_24 is not None
    assert deadline_24.day == 9
    assert deadline_24.hour == 0
    assert deadline_24.minute == 0

    # Normal hour 22
    deadline_22 = _calc_deadline(local, 22)
    assert deadline_22 is not None
    assert deadline_22.day == 8
    assert deadline_22.hour == 22

    # None
    assert _calc_deadline(local, None) is None


def test_khutbah_family_prompt_and_i18n():
    from khatmsaz.bot.handlers.member_commitment import _family_prompt
    from khatmsaz.i18n import t

    key = _family_prompt("commit.ask_times_per_period", "KHUTBAH")
    assert key == "commit.ask_times_per_period.khutbah"

    period_these_days = t("commit.period.these_days", "fa")
    assert period_these_days == "روزهای انتخابی"

    prompt_text = t(key, "fa", period=period_these_days)
    assert "چند بخش از خطبه را می‌خواهید در روزهای انتخابی بخوانید؟" in prompt_text

    unit_khutbah = t("commit.unit.khutbah", "fa")
    assert unit_khutbah == "بخش"


def test_khutbah_share_label_and_ranges():
    from khatmsaz.bot.member_copy import share_label

    label_single = share_label("khutbah", start=1, end=1, lang="fa")
    assert label_single == "بخش 1 از خطبه"

    label_range = share_label("khutbah", start=1, end=2, lang="fa")
    assert label_range == "بخش 1 تا 2 از خطبه"


@pytest.mark.asyncio
async def test_notify_adapter_target_message_supports_video():
    from unittest.mock import AsyncMock, MagicMock, patch
    from khatmsaz.bot import notify_adapter
    from khatmsaz.modules.identity.models import Platform

    mock_bot = MagicMock()
    mock_bot.send_video = AsyncMock(return_value=MagicMock(message_id=99))
    mock_bot.khatmsaz_platform = Platform.TELEGRAM

    mock_registry = MagicMock()
    mock_registry.get_creator_bot.return_value = mock_bot
    mock_registry.get_by_instance_id.return_value = mock_bot

    collected = []
    async def receipt_sender(method, **kwargs):
        collected.append((method, kwargs))
        return MagicMock(message_id=len(collected))

    # Test delivery using send_devotional_content with mock khatm
    with patch("khatmsaz.core.bot_registry.get_registry", return_value=mock_registry):
        mock_session = AsyncMock()
        mock_khatm = MagicMock()
        mock_khatm.description = None
        mock_khatm.title = "خطبه فدکیه"

        with patch("khatmsaz.modules.content.service.resolve_khatm_devotional_source", AsyncMock(return_value=(None, "khutbah-fadakiah"))):
            with patch("khatmsaz.modules.content.service.get_devotional_asset", AsyncMock(return_value=MagicMock(title="خطبه فدکیه", text_body=None))):
                with patch("khatmsaz.modules.content.service.list_devotional_video_pages", AsyncMock(return_value=[
                    MagicMock(page_number=1, asset_ref="video_file_id_1"),
                    MagicMock(page_number=2, asset_ref="video_file_id_2"),
                ])):
                    result = await notify_adapter.send_devotional_content(
                        mock_session, "TELEGRAM", "123456", khatm=mock_khatm, lang="fa",
                        receipt_sender=receipt_sender, page_numbers=[1],
                    )
                    assert result is True
                    assert len(collected) == 1
                    assert collected[0][0] == "send_video"
                    assert collected[0][1]["video"] == "video_file_id_1"
                    assert "بخش 1" in collected[0][1]["caption"]


@pytest.mark.asyncio
async def test_deliver_devotional_media_defaults_to_single_part_when_no_page_numbers():
    from unittest.mock import AsyncMock, MagicMock, patch
    from khatmsaz.bot.handlers import devotional
    from khatmsaz.modules.identity.models import Platform

    collected = []
    mock_message = MagicMock()
    mock_message.answer_video = AsyncMock(side_effect=lambda video, caption=None: collected.append((video, caption)))
    mock_message.bot = MagicMock()

    mock_session = AsyncMock()
    asset = MagicMock(title="خطبه فدکیه", text_body=None)
    with patch("khatmsaz.modules.content.service.list_devotional_video_pages", AsyncMock(return_value=[
        MagicMock(page_number=1, asset_ref="video_file_id_1"),
        MagicMock(page_number=2, asset_ref="video_file_id_2"),
        MagicMock(page_number=3, asset_ref="video_file_id_3"),
    ])):
        res = await devotional.deliver_devotional_media(
            mock_session, mock_message, slug="khutbah-fadakiah", asset=asset,
            platform=Platform.TELEGRAM, lang="fa", page_numbers=None,
        )
        assert res is True
        # Must only send 1 video (part 1), never all 3 videos!
        assert len(collected) == 1
        assert collected[0][0] == "video_file_id_1"
        assert "بخش 1" in collected[0][1]


@pytest.mark.asyncio
async def test_occurrence_adapter_self_heals_legacy_khutbah_occurrence():
    from unittest.mock import AsyncMock, MagicMock, patch
    from khatmsaz.bot import occurrence_adapter
    from khatmsaz.modules.identity.models import Platform

    mock_bot = MagicMock()
    mock_bot.khatmsaz_platform = Platform.TELEGRAM
    mock_bot.khatmsaz_language = "fa"

    mock_part = MagicMock(id=uuid4(), user_id=123, khatm_id=uuid4())
    mock_khatm = MagicMock(id=mock_part.khatm_id, template_type="SALAWAT")
    
    # Legacy occurrence: content_spec has no ranges, but has 5 stored components for amount=1
    mock_occurrence = MagicMock(
        id=uuid4(),
        amount=1,
        unit="COUNT",
        bot_instance_id=uuid4(),
        content_spec={"delivery_components": [{"method": "send_video"}] * 5},
    )

    captured_page_numbers = []
    async def mock_send_devotional_content(*args, **kwargs):
        captured_page_numbers.extend(kwargs.get("page_numbers") or [])
        sender = kwargs.get("receipt_sender")
        if sender:
            await sender("send_video", video="vid1", caption="بخش 1")
        return True

    mock_session = AsyncMock()
    mock_bot.send_video = AsyncMock(return_value=MagicMock(message_id=101))
    # Mock route to return mock_bot
    with patch("khatmsaz.bot.occurrence_adapter.route", AsyncMock(return_value=(mock_bot, 123456))):
        with patch("khatmsaz.bot.occurrence_adapter.repository.list_messages", AsyncMock(return_value=[])):
            with patch("khatmsaz.bot.occurrence_adapter.service.record_message", AsyncMock()):
                with patch("khatmsaz.bot.occurrence_adapter.send_control", AsyncMock(return_value=True)):
                    with patch("khatmsaz.modules.settings.service.get_or_create", AsyncMock(return_value=MagicMock(language="fa"))):
                        with patch("khatmsaz.bot.member_copy.content_family", AsyncMock(return_value="khutbah")):
                            with patch("khatmsaz.modules.content.service.resolve_khatm_devotional_source", AsyncMock(return_value=(None, "khutbah-fadakiah"))):
                                with patch("khatmsaz.modules.content.service.list_devotional_video_pages", AsyncMock(return_value=[
                                    MagicMock(page_number=i) for i in range(1, 6)
                                ])):
                                    with patch("khatmsaz.bot.notify_adapter.send_devotional_content", side_effect=mock_send_devotional_content):
                                        # Mock scalar to return 0 completed counts
                                        mock_session.scalar.return_value = 0
                                        ok = await occurrence_adapter.deliver_occurrence(
                                            mock_session, mock_part, mock_khatm, mock_occurrence, now=MagicMock()
                                        )
                                        assert ok is True
                                        # Stored components was reset and only 1 section was passed
                                        assert captured_page_numbers == [1]
                                        assert mock_occurrence.content_spec["ranges"] == [[1, 1]]
                                        assert mock_occurrence.content_spec["family"] == "khutbah"


def test_khutbah_commitment_preview_states_total_goal_not_per_member():
    khatm = Khatm(
        id=uuid4(),
        title="ختم خطبه فدکیه حضرت فاطمه زهرا (س)",
        template_type=KhatmTemplateType.SALAWAT,
        khatm_type=KhatmTypeEnum.COMMITMENT,
        repetition_target=110,
        niyyat="ظهور امام زمان عجل الله تعالی فرجه الشریف",
    )
    preview = build_join_preview_message(
        khatm,
        creator_name="خدمتگزاران تک",
        member_count=3,
        lang="fa",
        category_title="خطبه فدکیه حضرت فاطمه زهرا (س)",
        category_group="KHUTBAH",
    )
    assert "هدف کل ختم: 110 مرتبه" in preview
    assert "متعهد می‌شید 110 مرتبه انجام بدید" not in preview
    assert "سهم انتخابی خود را پس از عضویت متعهد می‌شوید" in preview


def test_done_button_label_returns_report_recitation():
    from types import SimpleNamespace
    from khatmsaz.bot.member_copy import done_button_label
    from khatmsaz.bot.occurrence_adapter import keyboard

    # Fallback labels when no share details are passed
    assert done_button_label("khutbah", "fa") == "✅ اعلام انجام قرائت"
    assert done_button_label("quran", "fa") == "✅ اعلام انجام قرائت"
    assert done_button_label("dua", "fa") == "✅ اعلام انجام قرائت دعا"

    # Customized dynamic labels when share details are passed
    assert done_button_label("quran", "fa", start=124, end=126) == "✅ اعلام ثبت قرائت صفحه 124 تا 126"
    assert done_button_label("quran", "fa", start=124, end=124) == "✅ اعلام ثبت قرائت صفحه 124"
    assert done_button_label("salawat", "fa", count=100) == "✅ اعلام ثبت قرائت 100 صلوات"
    assert (
        done_button_label("khutbah", "fa", start=3, end=4, title="ختم خطبه فدکیه حضرت فاطمه زهرا (س)")
        == "✅ اعلام ثبت قرائت بخش 3 و 4 خطبه فدکیه"
    )
    assert (
        done_button_label("khutbah", "fa", start=3, end=3, title="ختم خطبه فدکیه حضرت فاطمه زهرا (س)")
        == "✅ اعلام ثبت قرائت بخش 3 خطبه فدکیه"
    )
    assert (
        done_button_label("khutbah", "fa", start=1, end=3, title="ختم خطبه غدیریه")
        == "✅ اعلام ثبت قرائت بخش 1 تا 3 خطبه غدیریه"
    )
    assert done_button_label("ziyarat", "fa", count=1, title="ختم زیارت عاشورا") == "✅ اعلام ثبت قرائت 1 دور زیارت عاشورا"
    assert done_button_label("dua", "fa", count=3, title="ختم دعای عهد") == "✅ اعلام ثبت قرائت 3 دور دعای عهد"
    assert done_button_label("laan", "fa", count=100) == "✅ اعلام ثبت قرائت 100 مرتبه ذکر لعن"

    # Verify occurrence_adapter.keyboard builds dynamic button text from occurrence + khatm
    occ_khutbah = SimpleNamespace(
        id=uuid4(),
        unit="COUNT",
        amount=2,
        content_spec={"family": "khutbah", "language": "fa", "ranges": [[3, 4]]},
    )
    khatm_khutbah = SimpleNamespace(title="ختم خطبه فدکیه حضرت فاطمه زهرا (س)")
    kb = keyboard(occ_khutbah, khatm_khutbah)
    assert kb.inline_keyboard[0][0].text == "✅ اعلام ثبت قرائت بخش 3 و 4 خطبه فدکیه"


@pytest.mark.asyncio
async def test_khutbah_sections_advance_like_quran_even_when_prior_shares_uncompleted():
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, MagicMock, patch
    from khatmsaz.modules.share_occurrence.delivery import allocate_khutbah_section_range

    part_id = uuid4()
    khatm = SimpleNamespace(id=uuid4(), title="ختم خطبه فدکیه حضرت فاطمه زهرا (س)")
    stored_occurrences = []

    class FakeResult:
        def scalars(self):
            return list(stored_occurrences)

    session = MagicMock()
    session.execute = AsyncMock(side_effect=lambda *a, **kw: FakeResult())
    session.flush = AsyncMock()

    with patch("khatmsaz.modules.content.service.resolve_khatm_devotional_source", AsyncMock(return_value=(None, "khutbah-fadakiah"))):
        with patch("khatmsaz.modules.content.service.list_devotional_video_pages", AsyncMock(return_value=[
            MagicMock(page_number=i) for i in range(1, 6)
        ])):
            # Day 1: 2 sections -> (1, 2)
            s1, e1 = await allocate_khutbah_section_range(session, part_id, khatm, 2)
            assert (s1, e1) == (1, 2)
            stored_occurrences.append(SimpleNamespace(
                id=uuid4(), amount=2, completed_at=None, content_spec={"ranges": [[s1, e1]], "family": "khutbah"},
            ))

            # Day 2 (Day 1 still uncompleted!): advances to (3, 4)
            s2, e2 = await allocate_khutbah_section_range(session, part_id, khatm, 2)
            assert (s2, e2) == (3, 4)
            stored_occurrences.append(SimpleNamespace(
                id=uuid4(), amount=2, completed_at=None, content_spec={"ranges": [[s2, e2]], "family": "khutbah"},
            ))

            # Day 3 (Days 1 & 2 still uncompleted!): advances to (5, 5)
            s3, e3 = await allocate_khutbah_section_range(session, part_id, khatm, 2)
            assert (s3, e3) == (5, 5)
            stored_occurrences.append(SimpleNamespace(
                id=uuid4(), amount=2, completed_at=None, content_spec={"ranges": [[s3, e3]], "family": "khutbah"},
            ))

            # Day 4: wraps cleanly to next cycle (1, 2)
            s4, e4 = await allocate_khutbah_section_range(session, part_id, khatm, 2)
            assert (s4, e4) == (1, 2)


@pytest.mark.asyncio
async def test_khutbah_self_heals_colliding_uncompleted_occurrences():
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, MagicMock, patch
    from khatmsaz.modules.share_occurrence.delivery import allocate_khutbah_section_range

    part_id = uuid4()
    khatm = SimpleNamespace(id=uuid4(), title="ختم خطبه فدکیه حضرت فاطمه زهرا (س)")
    occ1 = SimpleNamespace(id=uuid4(), amount=2, completed_at="2026-10-07", content_spec={"ranges": [[1, 2]], "family": "khutbah"})
    occ2 = SimpleNamespace(id=uuid4(), amount=2, completed_at=None, content_spec={"ranges": [[3, 4]], "family": "khutbah"})
    # Legacy bug caused occ3 to also have [[3, 4]] while occ2 was uncompleted
    occ3 = SimpleNamespace(id=uuid4(), amount=2, completed_at=None, content_spec={"ranges": [[3, 4]], "family": "khutbah"})

    class FakeResult:
        def scalars(self):
            return [occ1, occ2, occ3]

    session = MagicMock()
    session.execute = AsyncMock(side_effect=lambda *a, **kw: FakeResult())
    session.flush = AsyncMock()

    with patch("khatmsaz.modules.content.service.resolve_khatm_devotional_source", AsyncMock(return_value=(None, "khutbah-fadakiah"))):
        with patch("khatmsaz.modules.content.service.list_devotional_video_pages", AsyncMock(return_value=[
            MagicMock(page_number=i) for i in range(1, 6)
        ])):
            await allocate_khutbah_section_range(session, part_id, khatm, 2)
            assert occ2.content_spec["ranges"] == [[3, 4]]
            assert occ3.content_spec["ranges"] == [[5, 5]]


@pytest.mark.asyncio
async def test_khutbah_open_prepare_numeric_allocates_multiple_sections_without_reservation():
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, MagicMock, patch
    from khatmsaz.modules.share_occurrence import delivery
    from uuid import uuid4

    test_user_id = uuid4()
    part = SimpleNamespace(
        id=uuid4(),
        khatm_id=uuid4(),
        user_id=test_user_id,
        is_committed=False,
        status="ACTIVE",
        joined_via_bot_instance_id=uuid4(),
    )
    khatm = SimpleNamespace(
        id=part.khatm_id,
        khatm_type="OPEN",
        template_type="SALAWAT",
        repetition_target=5,
        status="ACTIVE",
        commitment_policy="MEMBER_CHOICE",
        title="ختم خطبه فدکیه",
        content_category_id=uuid4(),
        starts_at=None,
    )

    session = MagicMock()
    with (
        patch("khatmsaz.modules.khatm.service.has_started", return_value=True),
        patch("khatmsaz.modules.participation.repository.get_by_id", AsyncMock(return_value=part)),
        patch("khatmsaz.modules.participation.repository.get_by_id_for_update", AsyncMock(return_value=part)),
        patch("khatmsaz.modules.khatm.service.get_khatm_for_update", AsyncMock(return_value=khatm)),
        patch("khatmsaz.modules.share_occurrence.repository.list_outstanding", AsyncMock(return_value=[])),
        patch("khatmsaz.modules.open_contribution.repository.total_for_khatm", AsyncMock(return_value=0)),
        patch("khatmsaz.bot.member_copy.content_family", AsyncMock(return_value="khutbah")),
        patch("khatmsaz.modules.share_occurrence.delivery.allocate_khutbah_section_range", AsyncMock(return_value=(1, 2))),
        patch("khatmsaz.modules.share_occurrence.service.create_once", AsyncMock(return_value=(
            SimpleNamespace(
                id=uuid4(), amount=2, reservation_id=None, committed=False,
                source_key="open:test", content_spec={"ranges": [[1, 2]], "family": "khutbah"},
            ), True
        ))),
    ):
        occ = await delivery.prepare_numeric(
            session, part.id, 2, user_id=test_user_id, bot_instance_id=part.joined_via_bot_instance_id
        )
        assert occ is not None
        assert occ.amount == 2
        assert occ.reservation_id is None
        assert occ.committed is False
        assert occ.content_spec["ranges"] == [[1, 2]]


@pytest.mark.asyncio
async def test_khutbah_record_progress_does_not_close_after_one_section():
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, MagicMock, patch
    from khatmsaz.modules.share_occurrence import delivery
    from uuid import uuid4

    part = SimpleNamespace(id=uuid4(), khatm_id=uuid4())
    khatm = SimpleNamespace(
        id=part.khatm_id,
        repetition_target=1,  # Legacy target: 1 round stored as 1
        status="ACTIVE",
    )
    occ = SimpleNamespace(
        id=uuid4(),
        amount=1,
        unit="COUNT",
        content_spec={"ranges": [[1, 1]], "family": "khutbah"},
    )

    session = MagicMock()
    with patch("khatmsaz.modules.khatm.service.get_khatm", AsyncMock(return_value=khatm)):
        with patch("khatmsaz.bot.member_copy.content_family", AsyncMock(return_value="khutbah")):
            with patch("khatmsaz.modules.allocation.repository.complete_portion", AsyncMock()):
                # Simulating reading section 1: total becomes 1 out of effective 5
                with patch("khatmsaz.modules.open_contribution.service.log_contribution", AsyncMock(return_value=(1, 0, 1))):
                    with patch("khatmsaz.modules.khatm.service.complete_khatm", AsyncMock()) as complete_mock:
                        with patch("khatmsaz.modules.advertising.service.accrue_first_completed_action", AsyncMock()):
                            await delivery.record_progress(session, part, occ)
                            # Khatm must NOT be completed after 1 section!
                            complete_mock.assert_not_called()

                # Simulating reading section 5: total reaches 5 out of effective 5
                with patch("khatmsaz.modules.open_contribution.service.log_contribution", AsyncMock(return_value=(1, 0, 5))):
                    with patch("khatmsaz.modules.khatm.service.complete_khatm", AsyncMock()) as complete_mock:
                        with patch("khatmsaz.modules.advertising.service.accrue_first_completed_action", AsyncMock()):
                            await delivery.record_progress(session, part, occ)
                            # Khatm completes when all 5 sections of the round are done!
                            complete_mock.assert_awaited_once_with(session, khatm.id)


def test_khutbah_video_caption_preserves_official_links():
    from khatmsaz.modules.content import service
    from types import SimpleNamespace

    for part_num in range(1, 6):
        vid = SimpleNamespace(page_number=part_num, reciter_label=None)
        caption = service.resolve_devotional_video_caption("khutbah-fadakiah", "خطبه فدکیه", vid)
        assert f"قسمت {part_num}" in caption or f"بخش {part_num}" in caption
        assert "khedmatgozaran.com" in caption
        assert "کلیپ_تصویری_خطابه_فدک" in caption


@pytest.mark.asyncio
async def test_open_khatm_prepare_returns_none_in_automated_scan():
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, patch
    from khatmsaz.modules.share_occurrence import delivery
    from uuid import uuid4

    part = SimpleNamespace(id=uuid4(), khatm_id=uuid4(), commitment_mode="REGULAR", joined_via_bot_instance_id=uuid4())
    khatm = SimpleNamespace(id=part.khatm_id, khatm_type="OPEN", template_type="SALAWAT")

    session = AsyncMock()
    with patch("khatmsaz.modules.participation.repository.get_by_id", AsyncMock(return_value=part)):
        with patch("khatmsaz.modules.khatm.service.get_khatm_for_update", AsyncMock(return_value=khatm)):
            with patch("khatmsaz.modules.participation.repository.get_by_id_for_update", AsyncMock(return_value=part)):
                # Automated scan (manual=False) must never auto-prepare daily deliveries for OPEN khatms!
                result = await delivery.prepare(session, part.id, manual=False)
                assert result is None


@pytest.mark.asyncio
async def test_deadline_reminder_triggers_two_hours_before_midnight():
    from types import SimpleNamespace
    from unittest.mock import AsyncMock, patch
    from datetime import datetime, timezone, timedelta
    from khatmsaz.modules.share_occurrence import delivery
    from khatmsaz.i18n import t
    from uuid import uuid4

    part = SimpleNamespace(id=uuid4(), khatm_id=uuid4())
    khatm = SimpleNamespace(id=part.khatm_id, title="ختم صلوات", template_type="SALAWAT")
    
    # Midnight deadline: 2026-10-10 24:00 (i.e. 2026-10-11 00:00)
    deadline = datetime(2026, 10, 11, 0, 0, tzinfo=timezone.utc)
    occurrence = SimpleNamespace(
        id=uuid4(),
        committed=True,
        delivered_at=datetime(2026, 10, 10, 9, 0, tzinfo=timezone.utc),
        deadline_at=deadline,
        amount=100,
        unit="COUNT",
        content_spec={"family": "salawat", "language": "fa"},
    )

    controls_sent = []
    async def fake_send_control(session, part, khatm, occ, purpose, *, now):
        controls_sent.append((purpose, now))
        return True

    session = AsyncMock()
    with (
        patch("khatmsaz.modules.participation.repository.get_by_id", AsyncMock(return_value=part)),
        patch("khatmsaz.modules.khatm.service.get_khatm", AsyncMock(return_value=khatm)),
        patch("khatmsaz.modules.notification.service.get_preference", AsyncMock(return_value=None)),
        patch("khatmsaz.modules.share_occurrence.repository.list_outstanding", AsyncMock(return_value=[occurrence])),
        patch("khatmsaz.bot.occurrence_adapter.send_control", side_effect=fake_send_control),
    ):
        # 3 hours before deadline (21:00) -> DEADLINE should not trigger yet
        at_21 = deadline - timedelta(hours=3)
        await delivery.remind(session, part.id, now=at_21)
        assert len([c for c in controls_sent if c[0] == "DEADLINE"]) == 0

        # Exactly 2 hours before deadline (22:00) -> DEADLINE MUST trigger
        at_22 = deadline - timedelta(hours=2)
        await delivery.remind(session, part.id, now=at_22)
        assert len([c for c in controls_sent if c[0] == "DEADLINE"]) == 1

    # Verify Persian copy contains the friendly 2-hour reminder message
    text = t("share.deadline", "fa")
    assert "۲ ساعت تا پایان مهلت امروز باقی مانده است" in text


@pytest.mark.asyncio
async def test_khutbah_rollover_and_progression():
    from khatmsaz.modules.share_occurrence import delivery
    from uuid import uuid4
    from unittest.mock import MagicMock, AsyncMock, patch
    from types import SimpleNamespace

    test_user_id = uuid4()
    part = SimpleNamespace(
        id=uuid4(),
        user_id=test_user_id,
        khatm_id=uuid4(),
        status="ACTIVE",
        joined_via_bot_instance_id=uuid4(),
        is_committed=False,
        open_reading_next_page=5,
    )
    khatm = SimpleNamespace(
        id=part.khatm_id,
        khatm_type="OPEN",
        template_type="SALAWAT",
        repetition_target=5,
        status="ACTIVE",
        commitment_policy="MEMBER_CHOICE",
        title="ختم خطبه فدکیه حضرت فاطمه زهرا (س)",
        content_category_id=uuid4(),
        starts_at=None,
    )

    session = AsyncMock()
    with (
        patch("khatmsaz.modules.khatm.service.has_started", return_value=True),
        patch("khatmsaz.modules.participation.repository.get_by_id", AsyncMock(return_value=part)),
        patch("khatmsaz.modules.participation.repository.get_by_id_for_update", AsyncMock(return_value=part)),
        patch("khatmsaz.modules.khatm.service.get_khatm_for_update", AsyncMock(return_value=khatm)),
        patch("khatmsaz.modules.share_occurrence.repository.list_outstanding", AsyncMock(return_value=[])),
        patch("khatmsaz.modules.open_contribution.repository.total_for_khatm", AsyncMock(return_value=0)),
        patch("khatmsaz.bot.member_copy.content_family", AsyncMock(return_value="khutbah")),
        patch("khatmsaz.modules.share_occurrence.service.create_once", AsyncMock(side_effect=lambda s, **kw: (SimpleNamespace(id=uuid4(), **kw), True))),
    ):
        # User is at section 5 and requests 2 sections:
        # Rollover MUST happen: [[5, 5], [1, 1]] without truncating amount to 1!
        occ = await delivery.prepare_numeric(
            session, part.id, 2, user_id=test_user_id, bot_instance_id=part.joined_via_bot_instance_id
        )
        assert occ is not None
        assert occ.amount == 2
        assert occ.content_spec["ranges"] == [[5, 5], [1, 1]]

        # Now test delivery progression updating part.open_reading_next_page
        with (
            patch("khatmsaz.bot.occurrence_adapter.deliver_occurrence", AsyncMock(return_value=True)),
            patch("khatmsaz.modules.share_occurrence.service.mark_delivered", AsyncMock()),
            patch("khatmsaz.modules.khatm.service.get_khatm", AsyncMock(return_value=khatm)),
            patch("khatmsaz.modules.participation.repository.get_by_id", AsyncMock(return_value=part)),
        ):
            delivered = await delivery.deliver(session, occ)
            assert delivered is True
            # Since last section in ranges was 1, next page MUST be (1 % 5) + 1 = 2
            assert part.open_reading_next_page == 2

